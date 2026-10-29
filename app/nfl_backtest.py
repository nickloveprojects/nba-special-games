"""Check the projection model against games that already happened.

For each sampled player and each game he played this season, the model sees only the games before it and projects the
stat line; we compare with what he actually did. The model is scored against two naive guesses: his average so far and
his last game. Opponent adjustment is left out because past weeks' defense tables are not stored.

    python -m app.nfl_backtest [--players 150]
"""
from __future__ import annotations

import argparse
import random
from datetime import date

from . import nfl_feed as feed, projection
from .net import SourceError


def evaluate(players: list[tuple[str, list[dict]]], sims: int = 400) -> dict:
    """players: [(position, chronological game logs)]. Returns {stat label: metrics}."""
    acc: dict[str, dict] = {}
    for pos, logs in players:
        for i in range(projection.MIN_GAMES, len(logs)):
            g = logs[i]
            d = date.fromisoformat(g["date"])
            p = projection.project(pos, logs[:i], {}, "", d, i, "", sims=sims)
            if not p:
                continue
            prior = projection.recent(logs[:i], d)
            for (field, label, _k), line in zip(projection.STATS[pos], p["lines"]):
                actual = g["row"].get(field, 0.0)
                vals = [x["row"].get(field, 0.0) for x in prior]
                s = acc.setdefault(f"{pos} {label}", {"n": 0, "model": 0.0, "avg": 0.0, "last": 0.0, "in": 0})
                s["n"] += 1
                s["model"] += abs(line["proj"] - actual)
                s["avg"] += abs(sum(vals) / len(vals) - actual)
                s["last"] += abs(vals[0] - actual)
                s["in"] += line["lo"] <= actual <= line["hi"]
    return {k: {"n": v["n"], "model_mae": round(v["model"] / v["n"], 2), "avg_mae": round(v["avg"] / v["n"], 2),
                "last_mae": round(v["last"] / v["n"], 2), "range_hit": round(100 * v["in"] / v["n"])}
            for k, v in sorted(acc.items()) if v["n"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--players", type=int, default=150)
    a = ap.parse_args()
    conn = feed.connect()
    year, _week, _events = feed.current_week_events()
    rng = random.Random(7)
    pool = []
    for tid in feed.teams():
        try:
            pool += [p for p in feed.roster(conn, tid) if p["pos"] in projection.STATS]
        except SourceError:
            continue
    rng.shuffle(pool)
    sample = []
    for p in pool:
        if len(sample) >= a.players:
            break
        try:
            logs = [g for g in feed.career_logs(conn, p["id"], p["years"], year, max_seasons=2) if not g["post"]]
        except SourceError:
            continue
        if len(logs) >= 8:
            sample.append((p["pos"], logs))
    print(f"{len(sample)} players")
    for k, v in evaluate(sample).items():
        print(f"{k:14} n={v['n']:4}  model {v['model_mae']:6}  avg {v['avg_mae']:6}  last {v['last_mae']:6}  80% range hit {v['range_hit']}%")


if __name__ == "__main__":
    main()
