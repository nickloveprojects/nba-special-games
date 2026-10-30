"""One pre-game points / rebounds / assists projection per flagged NBA player.

This season's games lead. Games from earlier seasons count at a quarter of the weight, only games with his current team are used, and a player
with fewer than 3 games this season on his current team gets no projection. (Backtest on the start of 2025-26: 1-4% less error than the
old version over a player's first ten games, and no worse later; a model with no earlier-season games at all was about as accurate.)
Opponent defense is softened further by how few games it rests on: backtested, it improves accuracy only slightly, so it is a small nudge.

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
MIN_GAMES = 3           # games THIS season with his current team (that is where his minutes come from)
PRIOR_WEIGHT = 0.25     # weight of a game from an earlier season relative to one this season
OPP_SAMPLE_K = 10.0     # opponent factor is scaled by n / (n + K), n = games it is built from
MIN_MINUTES = 12.0      # weighted minutes a game; below this the box score is too random to project
SHRINK_MIN = 150.0      # minutes of his longer-run rate blended into the recent rate
OPP_STRENGTH = 0.5
OPP_CLAMP = (0.88, 1.12)
RANGE_SPREAD = 1.0
# Backtest (13,800 player-games, 2025-26 before mid-Feb): points projections ran high for big scorers and low for
# low scorers (projected 20-25: +0.65 too high; 25+: +0.89; under 10: -0.29), the usual pull of extreme projections
# back toward the middle. Points are pulled back by this share of their distance from the league-typical 11.
PTS_PULL = 0.055
PTS_CENTER = 11.0
STATS = (("pts", "Pts"), ("reb", "Reb"), ("ast", "Ast"))
NO_PROJECTION = ("out", "doubtful", "injured reserve", "suspended")


def opp_factors(table: dict, opp: str, group: str | None = None) -> dict:
    """{stat: factor} from what the opponent allows per game, softened. With a position group (G/F/C) the factor is
    the average of the team-wide ratio and the ratio for that position, so it agrees with the matchup grade on the card.
    Scaled down by how few games it rests on, so early in the season it barely moves a number."""
    out = {k: 1.0 for k, _ in STATS}
    if opp not in table or table[opp].get("n", 0) < 5 or len(table) < 8:
        return out
    n = table[opp]["n"]
    strength = OPP_STRENGTH * n / (n + OPP_SAMPLE_K)
    for k, _ in STATS:
        ratios = []
        for g in ("ALL", group) if group in ("G", "F", "C") else ("ALL",):
            vals = [t[g][k] for t in table.values() if t.get(g)]
            mean = sum(vals) / len(vals) if vals else 0
            if mean > 0 and table[opp].get(g):
                ratios.append(table[opp][g][k] / mean)
        if ratios:
            ratio = sum(ratios) / len(ratios)
            out[k] = min(OPP_CLAMP[1], max(OPP_CLAMP[0], 1 + strength * (ratio - 1)))
    return out


def season_start(today: date) -> str:
    return date(today.year if today.month >= 8 else today.year - 1, 8, 1).isoformat()


def usable(logs: list[dict], team: str | None, today: date) -> list[dict]:
    """Newest-first regular-season games before today with his current team (when the log says which team)."""
    keep = [g for g in logs if not g.get("playoff") and g["date"] < today.isoformat() and g.get("min", 0) > 0
            and (not team or not g.get("tm") or g["tm"] == team)]
    keep.sort(key=lambda g: g["date"], reverse=True)
    return keep[:HISTORY]


def project(logs: list[dict], team: str | None, factors: dict, today: date, seed: int,
            status: str = "", sims: int = 1000) -> dict | None:
    """Minutes and per-minute rate both come only from games with his current team: his role and usage there are what
    matter, and the backtest found no gain from borrowing other clubs' games."""
    if any(w in (status or "").lower() for w in NO_PROJECTION):
        return None
    start = season_start(today)
    mine = usable(logs, team, today)
    if sum(g["date"] >= start for g in mine) < MIN_GAMES:
        return None            # not enough games this season with this team: any number would lean on old data
    allg = mine                # rate and minutes both come from games with his current team
    cur = mine[:WINDOW]
    pw = lambda gs: [(1.0 if g["date"] >= start else PRIOR_WEIGHT) for g in gs]
    w = [0.5 ** (i / HALF_LIFE) * a for i, a in enumerate(pw(cur))]
    mins = sum(g["min"] * x for g, x in zip(cur, w)) / sum(w)
    if mins < MIN_MINUTES:
        return None
    rec = allg[:WINDOW]
    wr = [0.5 ** (i / HALF_LIFE) * a for i, a in enumerate(pw(rec))]
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
        if k == "pts":
            shift = PTS_PULL * (proj - PTS_CENTER)
            proj, lo, hi = proj - shift, lo - shift, hi - shift
        lines.append({"label": label, "proj": round(proj, 1) if k != "pts" else round(proj),
                      "lo": round(max(0, lo)), "hi": round(hi)})
    return {"lines": lines, "games_used": sum(g["date"] >= start for g in cur), "minutes": round(mins), "sims": sims,
            "opp_factor": round(factors.get("pts", 1.0), 2)}
