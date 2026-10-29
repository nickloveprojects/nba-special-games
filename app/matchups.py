"""Matchup grades: how much each defense gives up to a player's position, from this season's real box scores.
For every finished regular-season game we add up the points, rebounds and assists each team's players scored by
position group (guard / forward / center) and credit them to the OTHER team's defense. Then we rank the 30 teams.
Green = the opponent gives up a lot of that stat to that position, yellow = average, red = tough."""
import json
import logging
from datetime import date, datetime, timedelta

from . import config
from .net import NotFound, SourceError
from .sources import espn
from .teams_geo import abbr, team_id

log = logging.getLogger("nba")
STATS = ("pts", "reb", "ast")
LABEL = {"pts": "points", "reb": "rebounds", "ast": "assists"}
WHO = {"G": "guards", "F": "forwards", "C": "centers", "ALL": "players"}
GROUPS = {"PG": "G", "SG": "G", "G": "G", "G-F": "G", "SF": "F", "PF": "F", "F": "F", "F-G": "F", "F-C": "F",
          "C": "C", "C-F": "C"}


def group(pos: str | None) -> str:
    return GROUPS.get((pos or "").upper(), "ALL")


def _num(x) -> int:
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return 0


def parse_box(data: dict) -> dict:
    """ESPN game summary -> {TEAM: {"opp": TEAM, "G": {pts,reb,ast}, "F": {...}, "C": {...}}} (what each team's players produced)."""
    out = {}
    for t in (data.get("boxscore") or {}).get("players") or []:
        tid = team_id((t.get("team") or {}).get("abbreviation"))
        if not tid:
            return {}
        sums = {g: dict.fromkeys(STATS, 0) for g in ("G", "F", "C")}
        for block in t.get("statistics") or []:
            names = block.get("names") or []
            for a in block.get("athletes") or []:
                if a.get("didNotPlay") or not a.get("stats"):
                    continue
                row = dict(zip(names, a["stats"]))
                g = group(((a.get("athlete") or {}).get("position") or {}).get("abbreviation"))
                if g == "ALL":
                    g = "F"   # unknown position: counted in the overall totals through "F" (rare)
                for k, n in (("pts", "PTS"), ("reb", "REB"), ("ast", "AST")):
                    sums[g][k] += _num(row.get(n))
        out[abbr(tid)] = sums
    if len(out) != 2:
        return {}
    a, b = list(out)
    out[a]["opp"], out[b]["opp"] = b, a
    return out


def build_table(boxes: list[dict]) -> dict:
    """boxes: list of parse_box results. -> {TEAM: {"n": games, "ALL": {pts,reb,ast per game allowed}, "G":..., "F":..., "C":...}}"""
    tot = {}
    for box in boxes:
        for team, d in box.items():
            opp = d["opp"]
            t = tot.setdefault(opp, {"n": 0, **{g: dict.fromkeys(STATS, 0) for g in ("ALL", "G", "F", "C")}})
            t["n"] += 1
            for g in ("G", "F", "C"):
                for k in STATS:
                    t[g][k] += d[g][k]
                    t["ALL"][k] += d[g][k]
    return {team: {"n": t["n"], **{g: {k: round(t[g][k] / t["n"], 1) for k in STATS} for g in ("ALL", "G", "F", "C")}}
            for team, t in tot.items() if t["n"]}


def _letter(score: float) -> str:
    return "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D" if score >= 20 else "F"


def _color(pct: float) -> str:
    return "green" if pct >= 2 / 3 else "yellow" if pct >= 1 / 3 else "red"


def _ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def matchup(table: dict, opp: str, pos: str | None) -> dict | None:
    """Grade for a player at position `pos` facing team `opp`. None when the team has no games yet."""
    if opp not in table:
        return None
    g = group(pos)
    teams = list(table)
    n_teams = len(teams)
    stats, pcts = {}, {}
    for k in STATS:
        vals = sorted((table[t][g][k] for t in teams), reverse=True)
        v = table[opp][g][k]
        rank = vals.index(v) + 1                      # 1 = gives up the most of this stat
        pct = 1 - (rank - 1) / (n_teams - 1) if n_teams > 1 else 0.5
        stats[k] = {"value": v, "rank": rank, "of": n_teams, "color": _color(pct)}
        pcts[k] = pct
    score = round(sum(pcts.values()) / len(pcts) * 100)
    best = max(STATS, key=lambda k: (pcts[k], -STATS.index(k)))
    b = stats[best]
    return {"group": g, "games": table[opp]["n"], "stats": stats, "score": score, "grade": _letter(score),
            "color": _color(score / 100), "best": best,
            "note": f"{abbr(team_id(opp))} gives up the {_ordinal(b['rank'])}-most {LABEL[best]} to {WHO[g]} "
                    f"({b['value']} a game, {table[opp]['n']} games)."}


# --------------------------------------------------------------- data loading (cached in SQLite)
def _season_start(d: date) -> date:
    return date(d.year if d.month >= 10 else d.year - 1, 10, 1)


def load_boxes(conn, slate_date: date, warn) -> list[dict]:
    """Box-score summaries of every finished regular-season game before `slate_date` (each game is fetched once)."""
    today = datetime.now(espn.ET).date()
    day = _season_start(slate_date)
    while day < slate_date:
        done = conn.execute("SELECT 1 FROM box_days WHERE date=?", (day.isoformat(),)).fetchone()
        if not done:
            try:
                sb = espn._get(f"{espn.SITE}/scoreboard", {"dates": day.strftime("%Y%m%d")})
                for e in sb.get("events", []):
                    if e.get("season", {}).get("type") != 2 or not e["status"]["type"].get("completed"):
                        continue
                    gid = str(e["id"])
                    if conn.execute("SELECT 1 FROM box WHERE game_id=?", (gid,)).fetchone():
                        continue
                    try:
                        box = parse_box(espn._get(f"{espn.SITE}/summary", {"event": gid}))
                    except NotFound:
                        box = {}
                    conn.execute("INSERT OR REPLACE INTO box VALUES(?,?,?)", (gid, day.isoformat(), json.dumps(box)))
                if day < today - timedelta(days=2):
                    conn.execute("INSERT OR REPLACE INTO box_days VALUES(?)", (day.isoformat(),))
                conn.commit()
            except SourceError as e:
                warn.add("matchups", f"Matchup data incomplete for {day} ({e})")
        day += timedelta(days=1)
    return [json.loads(r["json"]) for r in conn.execute("SELECT json FROM box WHERE date<?", (slate_date.isoformat(),))
            if r["json"] != "{}"]
