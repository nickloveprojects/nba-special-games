"""One pre-game stat projection per flagged player.

Method: take the player's recent games (newest count the most), nudge them by how generous the opponent has been to his
position, then play the game 1,000 times by drawing from those games. The projection is the average of the simulations
and the range is the middle 80% of them. Touchdowns use a Poisson draw so "scores a TD" is a probability.

This is an estimate built from public box-score stats. It does not see sportsbook lines, weather, or depth-chart news
beyond the injury status ESPN lists, so treat it as one input, not a prediction to bet on.
"""
from __future__ import annotations

import math
import random
from datetime import date, datetime, timezone

SIMS = 1000
RECENT_GAMES = 10          # how many past games feed the model
HALF_LIFE = 5.0            # a game this many games ago counts half as much as the latest one
MAX_AGE_DAYS = 420         # ignore games older than this (about one season plus an offseason)
MIN_GAMES = 3
OPP_STRENGTH = 0.5         # how much of the opponent's gap from average is applied
OPP_CLAMP = (0.85, 1.15)
YARD_SPREAD = 1.25        # backtest: yardage ranges held 71-76% of results, so they are stretched toward 80%

# position -> [(gamelog field, label, matchup table key)]
STATS = {
    "QB": [("passingYards", "Pass yds", "pass_yds"), ("passingTouchdowns", "Pass TD", "pass_td"), ("rushingYards", "Rush yds", None)],
    "RB": [("rushingYards", "Rush yds", "rush_yds"), ("receptions", "Rec", None), ("receivingYards", "Rec yds", "rec_yds")],
    "WR": [("receptions", "Rec", "rec"), ("receivingYards", "Rec yds", "rec_yds")],
    "TE": [("receptions", "Rec", "rec"), ("receivingYards", "Rec yds", "rec_yds")],
}
TD_FIELDS = {"RB": ("rushingTouchdowns", "receivingTouchdowns"), "WR": ("receivingTouchdowns",), "TE": ("receivingTouchdowns",)}
# a player listed with one of these is not expected to play, so no projection is shown
NO_PROJECTION = ("out", "doubtful", "injured reserve", "suspended", "pup", "nfi")


def opp_factor(table: dict, opp: str, pos: str, key: str | None) -> float:
    """How much more (or less) than average this opponent allows to the position, softened and clamped."""
    if not key or opp not in table or len(table) < 8:
        return 1.0
    vals = [t[pos][key] for t in table.values() if pos in t and key in t[pos]]
    mean = sum(vals) / len(vals) if vals else 0
    if mean <= 0:
        return 1.0
    ratio = table[opp][pos][key] / mean
    return min(OPP_CLAMP[1], max(OPP_CLAMP[0], 1 + OPP_STRENGTH * (ratio - 1)))


def recent(logs: list[dict], today: date) -> list[dict]:
    """Newest-first list of usable games."""
    keep = [g for g in logs if (today - date.fromisoformat(g["date"])).days <= MAX_AGE_DAYS and g["date"] < today.isoformat()]
    return list(reversed(keep))[:RECENT_GAMES]


def _poisson(rng: random.Random, lam: float) -> int:
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def _pct(sorted_vals: list[float], q: float) -> float:
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(q * len(sorted_vals))))]


def _round(label: str, v: float) -> float:
    v = max(0.0, v)
    return round(v, 1) if label in ("Rec", "Pass TD") else round(v)


def project(pos: str, logs: list[dict], table: dict, opp: str, today: date, seed: int,
            status: str = "", sims: int = SIMS) -> dict | None:
    """Projection for one player, or None when there is too little to go on."""
    if pos not in STATS or any(w in (status or "").lower() for w in NO_PROJECTION):
        return None
    games = recent(logs, today)
    if len(games) < MIN_GAMES:
        return None
    w = [0.5 ** (i / HALF_LIFE) for i in range(len(games))]
    rng = random.Random(seed)
    picks = rng.choices(range(len(games)), weights=w, k=sims)
    lines = []
    for field, label, key in STATS[pos]:
        f = opp_factor(table, opp, pos, key)
        vals = sorted(games[i]["row"].get(field, 0.0) * f for i in picks)
        mean = sum(vals) / len(vals)
        lo, hi = _pct(vals, 0.1), _pct(vals, 0.9)
        if "yds" in label:
            lo, hi = mean - (mean - lo) * YARD_SPREAD, mean + (hi - mean) * YARD_SPREAD
        lines.append({"label": label, "proj": _round(label, mean), "lo": _round(label, lo), "hi": _round(label, hi)})
    out = {"lines": lines, "games_used": len(games), "sims": sims}
    if pos in TD_FIELDS:
        per_game = [sum(g["row"].get(k, 0.0) for k in TD_FIELDS[pos]) for g in games]
        lam = sum(a * b for a, b in zip(per_game, w)) / sum(w)
        f = opp_factor(table, opp, pos, STATS[pos][-1][2])
        lam *= f
        hit = sum(1 for _ in range(sims) if _poisson(rng, lam) >= 1) / sims
        out["td_prob"] = round(hit * 100)
    out["opp_factor"] = round(opp_factor(table, opp, pos, STATS[pos][0][2]), 2)
    return out


def started(tip_utc: str, now: datetime | None = None) -> bool:
    return datetime.fromisoformat(tip_utc) <= (now or datetime.now(timezone.utc))


def freeze(computed: dict | None, prior: dict | None, tip_utc: str, now: datetime | None = None) -> dict | None:
    """Before kickoff the fresh projection is used and stamped as open. After kickoff nothing is recomputed: the
    projection published before the game is kept and marked locked (None if there never was one)."""
    if not started(tip_utc, now):
        return {**computed, "locked": False} if computed else None
    return {**prior, "locked": True} if prior else None
