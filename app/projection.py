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

# position -> [(gamelog field, label, matchup table key, volume field, league yield per unit of volume)]
# League yields (2024-26 regular season) pull a thin sample toward the norm: a catch rate or yards per carry from a few
# games is mostly luck, while volume (targets, carries, attempts) carries over from week to week.
STATS = {
    "QB": [("passingYards", "Pass yds", "pass_yds", "passingAttempts", 7.07), ("passingTouchdowns", "Pass TD", "pass_td", "passingAttempts", 0.046),
           ("rushingYards", "Rush yds", None, "rushingAttempts", 4.51)],
    "RB": [("rushingYards", "Rush yds", "rush_yds", "rushingAttempts", 4.32), ("receptions", "Rec", None, "receivingTargets", 0.788),
           ("receivingYards", "Rec yds", "rec_yds", "receivingTargets", 5.87)],
    "WR": [("receptions", "Rec", "rec", "receivingTargets", 0.628), ("receivingYards", "Rec yds", "rec_yds", "receivingTargets", 7.95)],
    "TE": [("receptions", "Rec", "rec", "receivingTargets", 0.723), ("receivingYards", "Rec yds", "rec_yds", "receivingTargets", 7.27)],
}
SHRINK = 15.0              # weight, in units of volume, given to the league yield (backtest: 15 beat 0 and 40)
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


def recent(logs: list[dict], today: date, team_id: int | None = None) -> list[dict]:
    """Newest-first list of usable games. With team_id, only games he played for that club count, because his role,
    quarterback and offense were different anywhere else."""
    keep = [g for g in logs if (today - date.fromisoformat(g["date"])).days <= MAX_AGE_DAYS and g["date"] < today.isoformat()
            and (team_id is None or g.get("team_id") == team_id)]
    return list(reversed(keep))[:RECENT_GAMES]


MIN_USAGE = {"QB": 10.0, "RB": 3.0, "WR": 1.5, "TE": 1.5}   # weighted touches a game: attempts / carries + targets / targets


def _usage(pos: str, games: list[dict], w: list[float]) -> float:
    keys = {"QB": ("passingAttempts",), "RB": ("rushingAttempts", "receivingTargets")}.get(pos, ("receivingTargets",))
    return sum(sum(g["row"].get(k, 0.0) for k in keys) * x for g, x in zip(games, w)) / sum(w)


def _pct(sorted_vals: list[float], q: float) -> float:
    return sorted_vals[min(len(sorted_vals) - 1, max(0, int(q * len(sorted_vals))))]


def _round(label: str, v: float) -> float:
    v = max(0.0, v)
    return round(v, 1) if label in ("Rec", "Pass TD") else round(v)


def _shrink_scale(games: list[dict], w: list[float], field: str, vol_field: str, league: float) -> float:
    """Ratio that moves the weighted average to volume x shrunk yield, so thin-sample luck counts for less."""
    tw = sum(w)
    raw = sum(g["row"].get(field, 0.0) * x for g, x in zip(games, w)) / tw
    vol = sum(g["row"].get(vol_field, 0.0) * x for g, x in zip(games, w)) / tw
    if raw <= 0 or vol < 1.0:
        return 1.0
    y = sum(g["row"].get(field, 0.0) * x for g, x in zip(games, w))
    v = sum(g["row"].get(vol_field, 0.0) * x for g, x in zip(games, w))
    shrunk = vol * (y + SHRINK * league) / (v + SHRINK)
    return min(1.3, max(0.7, shrunk / raw))


def project(pos: str, logs: list[dict], table: dict, opp: str, today: date, seed: int,
            status: str = "", sims: int = SIMS, weather: float = 1.0, team_id: int | None = None) -> dict | None:
    """Projection for one player, or None when there is too little to go on."""
    if pos not in STATS or any(w in (status or "").lower() for w in NO_PROJECTION):
        return None
    games = recent(logs, today, team_id)
    if len(games) < MIN_GAMES:
        return None
    w = [0.5 ** (i / HALF_LIFE) for i in range(len(games))]
    if _usage(pos, games, w) < MIN_USAGE[pos]:
        return None            # a player with next to no touches lately: any number here would be noise
    rng = random.Random(seed)
    picks = rng.choices(range(len(games)), weights=w, k=sims)
    lines = []
    for field, label, key, vol_field, league in STATS[pos]:
        f = opp_factor(table, opp, pos, key) * (1.0 if field == "rushingYards" else weather)
        scale = _shrink_scale(games, w, field, vol_field, league)
        vals = sorted(games[i]["row"].get(field, 0.0) * f * scale for i in picks)
        mean = sum(vals) / len(vals)
        lo, hi = _pct(vals, 0.1), _pct(vals, 0.9)
        if "yds" in label:
            lo, hi = mean - (mean - lo) * YARD_SPREAD, mean + (hi - mean) * YARD_SPREAD
        lines.append({"label": label, "proj": _round(label, mean), "lo": _round(label, lo), "hi": _round(label, hi)})
    out = {"lines": lines, "games_used": len(games), "sims": sims}
    out["weather_factor"] = round(weather, 2)
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
