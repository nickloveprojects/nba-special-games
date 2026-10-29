"""One pre-game points / rebounds / assists projection per flagged NBA player.

Minutes are the biggest driver of an NBA box score, so the projection is: expected minutes with his current team (recent games count more)
x his per-minute rate (pulled toward his own longer-run rate so a hot or cold week counts for less) x how generous
the opponent has been to opposing teams, softened. Backtested on the 2025-26 regular season (12,800 player-games):
about 2% less error than a last-10-game average, with the longer window (about 20 games) beating shorter ones.
Tried and left out because they did not help on average: back-to-backs, pace, and a teammates-out boost.
The range is the middle 80% of 1,000 simulated games drawn from his recent games.
"""
from __future__ import annotations

import random
from datetime import date

HALF_LIFE = 10.0
WINDOW = 20             # recent games that carry weight
HISTORY = 60            # games used for his longer-run rate
MIN_GAMES = 3           # games with his current team (that is where his minutes come from)
MIN_MINUTES = 12.0      # weighted minutes a game; below this the box score is too random to project
SHRINK_MIN = 150.0      # minutes of his longer-run rate blended into the recent rate
OPP_STRENGTH = 0.5
OPP_CLAMP = (0.88, 1.12)
RANGE_SPREAD = 1.0
STATS = (("pts", "Pts"), ("reb", "Reb"), ("ast", "Ast"))
NO_PROJECTION = ("out", "doubtful", "injured reserve", "suspended")


def opp_factors(table: dict, opp: str) -> dict:
    """{stat: factor} from the opponent's per-game points/rebounds/assists allowed vs the league average."""
    out = {k: 1.0 for k, _ in STATS}
    if opp not in table or table[opp].get("n", 0) < 5 or len(table) < 8:
        return out
    for k, _ in STATS:
        vals = [t["ALL"][k] for t in table.values() if t.get("ALL")]
        mean = sum(vals) / len(vals) if vals else 0
        if mean > 0:
            ratio = table[opp]["ALL"][k] / mean
            out[k] = min(OPP_CLAMP[1], max(OPP_CLAMP[0], 1 + OPP_STRENGTH * (ratio - 1)))
    return out


def usable(logs: list[dict], team: str | None, today: date) -> list[dict]:
    """Newest-first regular-season games before today with his current team (when the log says which team)."""
    keep = [g for g in logs if not g.get("playoff") and g["date"] < today.isoformat() and g.get("min", 0) > 0
            and (not team or not g.get("tm") or g["tm"] == team)]
    keep.sort(key=lambda g: g["date"], reverse=True)
    return keep[:HISTORY]


def project(logs: list[dict], team: str | None, factors: dict, today: date, seed: int,
            status: str = "", sims: int = 1000) -> dict | None:
    """Minutes come only from games with his current team, since that is his role now. His per-minute rate uses all
    recent games, because scoring, rebounding and passing skill travel with a player."""
    if any(w in (status or "").lower() for w in NO_PROJECTION):
        return None
    mine = usable(logs, team, today)
    if len(mine) < MIN_GAMES:
        return None
    allg = usable(logs, None, today)
    cur = mine[:WINDOW]
    w = [0.5 ** (i / HALF_LIFE) for i in range(len(cur))]
    mins = sum(g["min"] * x for g, x in zip(cur, w)) / sum(w)
    if mins < MIN_MINUTES:
        return None
    rec = allg[:WINDOW]
    wr = [0.5 ** (i / HALF_LIFE) for i in range(len(rec))]
    sw = sum(wr)
    total_min = sum(g["min"] for g in allg)
    rng = random.Random(seed)
    picks = rng.choices(range(len(rec)), weights=wr, k=sims)
    lines = []
    for k, label in STATS:
        long_rate = sum(g[k] for g in allg) / total_min
        wmean_w = sw / len(rec)
        rate = (sum(g[k] * x for g, x in zip(rec, wr)) + SHRINK_MIN * long_rate * wmean_w) / \
               (sum(g["min"] * x for g, x in zip(rec, wr)) + SHRINK_MIN * wmean_w)
        proj = mins * rate * factors.get(k, 1.0)
        raw = sum(g[k] * x for g, x in zip(rec, wr)) / sw
        scale = proj / raw if raw > 0 else 1.0
        vals = sorted(max(0.0, rec[i][k] * scale) for i in picks)
        lo, hi = vals[int(0.1 * sims)], vals[min(sims - 1, int(0.9 * sims))]
        lo, hi = proj - (proj - lo) * RANGE_SPREAD, proj + (hi - proj) * RANGE_SPREAD
        lines.append({"label": label, "proj": round(proj, 1) if k != "pts" else round(proj),
                      "lo": round(max(0, lo)), "hi": round(hi)})
    return {"lines": lines, "games_used": len(cur), "minutes": round(mins), "sims": sims,
            "opp_factor": round(factors.get("pts", 1.0), 2)}
