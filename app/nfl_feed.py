"""ESPN NFL feeds (schedule, rosters, game logs, team history, transactions) with a small SQLite cache."""
import json
import logging
import re
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from . import config
from .net import NotFound, SourceError, get_json

log = logging.getLogger("nba")
SITE = "https://site.api.espn.com/apis/site/v2/sports/football/nfl"
WEB = "https://site.web.api.espn.com/apis/common/v3/sports/football/nfl"
HDR = {"User-Agent": "Mozilla/5.0 (compatible; backstory-sports)"}
ET = ZoneInfo(config.TZ)
DB_PATH = config.DATA / "nfl.sqlite"
GROUP = {"QB": "QB", "RB": "RB", "FB": "RB", "WR": "WR", "TE": "TE", "K": "K", "PK": "K"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS places(key TEXT PRIMARY KEY, label TEXT, lat REAL, lon REAL, source_url TEXT, found INTEGER, updated TEXT);
CREATE TABLE IF NOT EXISTS gl(athlete_id INTEGER, season INTEGER, fetched TEXT, json TEXT, PRIMARY KEY(athlete_id, season));
CREATE TABLE IF NOT EXISTS teamhist(athlete_id INTEGER PRIMARY KEY, fetched TEXT, json TEXT);
CREATE TABLE IF NOT EXISTS roster(team_id INTEGER PRIMARY KEY, fetched TEXT, json TEXT);
CREATE TABLE IF NOT EXISTS box(game_id TEXT PRIMARY KEY, json TEXT);
CREATE TABLE IF NOT EXISTS tx2(year INTEGER PRIMARY KEY, fetched TEXT, json TEXT);
"""

# Stadium coordinates (home venue of each club, ESPN abbreviations); used for hometown and career hometown games.
VENUE = {
    "ARI": (33.528, -112.263), "ATL": (33.755, -84.401), "BAL": (39.278, -76.623), "BUF": (42.774, -78.787),
    "CAR": (35.226, -80.853), "CHI": (41.862, -87.617), "CIN": (39.095, -84.516), "CLE": (41.506, -81.699),
    "DAL": (32.748, -97.093), "DEN": (39.744, -105.020), "DET": (42.340, -83.046), "GB": (44.501, -88.062),
    "HOU": (29.685, -95.411), "IND": (39.760, -86.164), "JAX": (30.324, -81.637), "KC": (39.049, -94.484),
    "LV": (36.091, -115.184), "LAC": (33.953, -118.339), "LAR": (33.953, -118.339), "MIA": (25.958, -80.239),
    "MIN": (44.974, -93.258), "NE": (42.091, -71.264), "NO": (29.951, -90.081), "NYG": (40.814, -74.074),
    "NYJ": (40.814, -74.074), "PHI": (39.901, -75.168), "PIT": (40.447, -80.016), "SF": (37.403, -121.970),
    "SEA": (47.595, -122.332), "TB": (27.976, -82.503), "TEN": (36.166, -86.771), "WSH": (38.908, -76.864)}
# Rough state centers, only used to skip geocoding players who were born far from the stadium.
STATE_CENTER = {
    "AL": (32.8, -86.8), "AK": (64.0, -150.0), "AZ": (34.2, -111.7), "AR": (34.9, -92.4), "CA": (37.2, -119.5),
    "CO": (39.0, -105.5), "CT": (41.6, -72.7), "DE": (39.0, -75.5), "DC": (38.9, -77.0), "FL": (28.6, -82.4),
    "GA": (32.7, -83.4), "HI": (20.8, -156.3), "ID": (44.4, -114.6), "IL": (40.0, -89.2), "IN": (39.9, -86.3),
    "IA": (42.1, -93.5), "KS": (38.5, -98.4), "KY": (37.5, -85.3), "LA": (31.1, -92.0), "ME": (45.3, -69.2),
    "MD": (39.0, -76.8), "MA": (42.3, -71.8), "MI": (44.3, -85.4), "MN": (46.3, -94.3), "MS": (32.7, -89.7),
    "MO": (38.4, -92.5), "MT": (47.0, -109.6), "NE": (41.5, -99.8), "NV": (39.3, -116.6), "NH": (43.7, -71.6),
    "NJ": (40.1, -74.7), "NM": (34.4, -106.1), "NY": (42.9, -75.5), "NC": (35.5, -79.4), "ND": (47.5, -100.5),
    "OH": (40.3, -82.8), "OK": (35.6, -97.5), "OR": (43.9, -120.6), "PA": (40.9, -77.8), "RI": (41.7, -71.5),
    "SC": (33.9, -80.9), "SD": (44.4, -100.2), "TN": (35.8, -86.3), "TX": (31.5, -99.3), "UT": (39.3, -111.7),
    "VT": (44.0, -72.7), "VA": (37.5, -78.8), "WA": (47.4, -120.5), "WV": (38.6, -80.6), "WI": (44.6, -89.9),
    "WY": (43.0, -107.5)}


def connect() -> sqlite3.Connection:
    config.DATA.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript(SCHEMA)
    return c


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _fresh(ts: str, hours: float) -> bool:
    return (_now() - datetime.fromisoformat(ts)) < timedelta(hours=hours)


def _get(url, params=None):
    time.sleep(config.SLEEP)
    return get_json(url, params=params, headers=HDR, retries=config.RETRIES, timeout=config.TIMEOUT)


# ------------------------------------------------------------------ schedule
def parse_events(data: dict) -> list[dict]:
    out = []
    for e in data.get("events", []):
        comp = e["competitions"][0]
        sides = {c["homeAway"]: c["team"] for c in comp["competitors"]}
        if "home" not in sides or "away" not in sides:
            continue
        tip = datetime.fromisoformat(e["date"].replace("Z", "+00:00"))
        v = comp.get("venue") or {}
        addr = v.get("address") or {}
        out.append({
            "game_id": str(e["id"]), "tip_utc": tip.isoformat(), "date": tip.astimezone(ET).date().isoformat(),
            "tip": tip.astimezone(ET).strftime("%-I:%M %p ET"), "week": (e.get("week") or {}).get("number"),
            "completed": bool(e["status"]["type"].get("completed")), "neutral": bool(comp.get("neutralSite")),
            "kind": {1: "Preseason", 2: "Regular season", 3: "Playoffs"}.get(e.get("season", {}).get("type"), "Game"),
            "arena": v.get("fullName", ""), "venue_city": addr.get("city", ""), "venue_state": addr.get("state", ""),
            "home": sides["home"], "away": sides["away"]})
    return out


def current_week_events() -> tuple[int, int, list[dict]]:
    """(season year, week, events) for the week being played; moves to the next week once every game is final."""
    sb = _get(f"{SITE}/scoreboard")
    year, week = sb["season"]["year"], sb["week"]["number"]
    ev = parse_events(sb)
    if ev and all(x["completed"] for x in ev):
        nxt = _get(f"{SITE}/scoreboard", {"week": week + 1, "seasontype": sb["season"]["type"]})
        e2 = parse_events(nxt)
        if e2:
            return year, week + 1, e2
    return year, week, ev


# ------------------------------------------------------------------ rosters
def roster(conn, team_id: int) -> list[dict]:
    """Official-roster skill players (QB/RB/WR/TE/K), backups included. Injured reserve and practice squad are left out."""
    r = conn.execute("SELECT fetched, json FROM roster WHERE team_id=?", (team_id,)).fetchone()
    if r and _fresh(r["fetched"], 12):
        data = json.loads(r["json"])
    else:
        try:
            data = _get(f"{SITE}/teams/{team_id}/roster")
        except SourceError:
            if not r:
                raise
            data = json.loads(r["json"])
        else:
            conn.execute("INSERT OR REPLACE INTO roster VALUES(?,?,?)", (team_id, _now().isoformat(timespec="seconds"), json.dumps(data)))
            conn.commit()
    out = []
    for grp in (data or {}).get("athletes", []):
        if grp.get("position") in ("injuredReserveOrOut", "suspended", "practiceSquad"):
            continue        # only the official roster: no injured reserve, no practice squad
        for a in grp.get("items", []):
            pos = GROUP.get(((a.get("position") or {}).get("abbreviation") or "").upper())
            if not pos or (a.get("status") or {}).get("type", "active") != "active":
                continue
            inj = ((a.get("injuries") or [{}])[0].get("status") or "").strip()
            if any(w in inj.lower() for w in ("reserve", "suspend", "pup", "nfi")):
                continue        # injured reserve etc: not playing this week
            bp = a.get("birthPlace") or {}
            out.append({"id": int(a["id"]), "name": a["fullName"], "pos": pos, "jersey": a.get("jersey") or "",
                        "dob": (a.get("dateOfBirth") or "")[:10], "city": bp.get("city", ""), "state": bp.get("state", ""),
                        "country": bp.get("country", ""), "years": (a.get("experience") or {}).get("years", 0) or 0,
                        "headshot": ((a.get("headshot") or {}).get("href")), "team_id": team_id,
                        "injury": inj})
    return out


# ------------------------------------------------------------------ game logs
def _num(x) -> float:
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return 0.0


def parse_gamelog(data: dict, season: int) -> list[dict]:
    names = data.get("names") or []
    meta = data.get("events") or {}
    out = []
    for st in data.get("seasonTypes") or []:
        post = "post" in (st.get("displayName") or "").lower()
        for cat in st.get("categories") or []:
            for ev in cat.get("events") or []:
                m = meta.get(str(ev["eventId"]))
                if not m:
                    continue
                row = {}
                for n, v in zip(names, ev.get("stats") or []):
                    if re.fullmatch(r"\d+-\d+", str(v)):          # kicking: "made-attempts"
                        mk, at = str(v).split("-")
                        row[n + ".made"], row[n + ".att"] = float(mk), float(at)
                    else:
                        row[n] = _num(v)
                tid = int((m.get("team") or {}).get("id") or 0)
                oid = int((m.get("opponent") or {}).get("id") or 0)
                d = datetime.fromisoformat(m["gameDate"].replace("Z", "+00:00")).astimezone(ET).date().isoformat()
                out.append({"gid": str(m["id"]), "date": d, "season": season, "post": post, "team_id": tid,
                            "opp_id": oid, "opp": (m.get("opponent") or {}).get("abbreviation", ""),
                            "home": m.get("atVs") == "vs", "home_id": int(m.get("homeTeamId") or 0),
                            "result": m.get("gameResult") or "", "week": m.get("week"), "row": row})
    return sorted(out, key=lambda g: g["date"])


def gamelog(conn, athlete_id: int, season: int, current: int) -> list[dict]:
    r = conn.execute("SELECT fetched, json FROM gl WHERE athlete_id=? AND season=?", (athlete_id, season)).fetchone()
    if r and (season < current or _fresh(r["fetched"], config.GAMELOG_TTL_HOURS)):
        return json.loads(r["json"])
    try:
        data = _get(f"{WEB}/athletes/{athlete_id}/gamelog", {"season": season})
        logs = parse_gamelog(data, season)
    except NotFound:
        logs = []
    except SourceError:
        if r:
            return json.loads(r["json"])
        raise
    conn.execute("INSERT OR REPLACE INTO gl VALUES(?,?,?,?)", (athlete_id, season, _now().isoformat(timespec="seconds"), json.dumps(logs)))
    conn.commit()
    return logs


def career_logs(conn, athlete_id: int, years: int, current: int, max_seasons=8) -> list[dict]:
    out = []
    for s in range(max(current - max(years, 0), current - max_seasons + 1), current + 1):
        out += gamelog(conn, athlete_id, s, current)
    return out


def past_teams(conn, athlete_id: int) -> dict[int, str]:
    """Every club the player has ever had stats with: {espn team id: abbreviation}. Cached for 30 days."""
    r = conn.execute("SELECT fetched, json FROM teamhist WHERE athlete_id=?", (athlete_id,)).fetchone()
    if r and _fresh(r["fetched"], 24 * 30):
        return {int(k): v for k, v in json.loads(r["json"]).items()}
    try:
        data = _get(f"{WEB}/athletes/{athlete_id}/stats")
        teams = {int(t["id"]): t["abbreviation"] for t in (data.get("teams") or {}).values()}
    except NotFound:
        teams = {}
    conn.execute("INSERT OR REPLACE INTO teamhist VALUES(?,?,?)", (athlete_id, _now().isoformat(timespec="seconds"), json.dumps(teams)))
    conn.commit()
    return teams


# ------------------------------------------------------------------ transactions (ESPN keeps a log per calendar year)
def transactions_year(conn, year: int, current_year: int) -> list[dict]:
    r = conn.execute("SELECT fetched, json FROM tx2 WHERE year=?", (year,)).fetchone()
    if r and _fresh(r["fetched"], 6 if year >= current_year else 24 * 60):
        return json.loads(r["json"])
    rows = []
    try:
        for pg in range(1, 40):
            d = _get(f"{SITE}/transactions", {"season": year, "limit": 500, "page": pg})
            for t in d.get("transactions") or []:
                if (t.get("description") or "").strip():
                    rows.append({"date": t["date"][:10], "team": t["team"]["abbreviation"],
                                 "name": t["team"].get("displayName", ""), "text": t["description"].strip()})
            if pg >= d.get("pageCount", 1):
                break
    except SourceError:
        if r:
            return json.loads(r["json"])
        raise
    conn.execute("INSERT OR REPLACE INTO tx2 VALUES(?,?,?)", (year, _now().isoformat(timespec="seconds"), json.dumps(rows)))
    conn.commit()
    return rows


def _sentences(text: str) -> list[str]:
    return [x.strip() + ("" if x.strip().endswith(".") else ".") for x in re.split(r"(?<=[a-z0-9\)])\.\s+(?=[A-Z])", text) if x.strip()]


# ------------------------------------------------------------------ box scores (for matchup grades)
def box_for_game(conn, gid: str) -> dict:
    r = conn.execute("SELECT json FROM box WHERE game_id=?", (gid,)).fetchone()
    if r:
        return json.loads(r["json"])
    try:
        d = _get(f"{SITE}/summary", {"event": gid})
        out = {}
        for t in (d.get("boxscore") or {}).get("players") or []:
            ab = t["team"]["abbreviation"]
            ppl = {}
            for blk in t.get("statistics") or []:
                keys = blk.get("keys") or []
                for a in blk.get("athletes") or []:
                    row = dict(zip(keys, a.get("stats") or []))
                    ppl.setdefault(a["athlete"]["id"], {}).update({blk["name"] + "." + k: v for k, v in row.items()})
            out[ab] = ppl
    except NotFound:
        out = {}
    conn.execute("INSERT OR REPLACE INTO box VALUES(?,?)", (gid, json.dumps(out)))
    conn.commit()
    return out


def finished_games(through_week: int) -> list[str]:
    """Game ids of every finished regular-season game before `through_week`."""
    ids = []
    for wk in range(1, through_week):
        try:
            ids += [e["game_id"] for e in parse_events(_get(f"{SITE}/scoreboard", {"week": wk, "seasontype": 2})) if e["completed"]]
        except SourceError:
            continue
    return ids


def teams() -> dict[int, dict]:
    """{espn id: {abbr, name, short, color, alt, logo}} for all 32 clubs."""
    d = _get(f"{SITE}/teams")
    out = {}
    for x in d["sports"][0]["leagues"][0]["teams"]:
        t = x["team"]
        out[int(t["id"])] = {"id": int(t["id"]), "abbr": t["abbreviation"], "name": t["displayName"],
                             "short": t.get("shortDisplayName") or t["name"], "color": "#" + (t.get("color") or "444444"),
                             "alt": "#" + (t.get("alternateColor") or "ffffff")}
    return out
