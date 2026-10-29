"""ESPN public JSON feeds: schedule, rosters (with birthdate + birthplace), career history, trades.
These are unofficial but stable, free, and reachable from cloud servers (unlike stats.nba.com)."""
import logging
import re
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from .. import config
from ..net import NotFound, get_json
from ..rules import norm_name
from ..teams_geo import ABBR_TO_ID, TEAMS, abbr, team_id, nick

log = logging.getLogger("nba")
SITE = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
WEB = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba"
HDR = {"User-Agent": "Mozilla/5.0 (compatible; nba-special-games)"}
ET = ZoneInfo(config.TZ)

ESPN_ID = {"ATL": 1, "BOS": 2, "NOP": 3, "CHI": 4, "CLE": 5, "DAL": 6, "DEN": 7, "DET": 8, "GSW": 9, "HOU": 10,
           "IND": 11, "LAC": 12, "LAL": 13, "MIA": 14, "MIL": 15, "MIN": 16, "BKN": 17, "NYK": 18, "ORL": 19,
           "PHI": 20, "PHX": 21, "POR": 22, "SAC": 23, "SAS": 24, "OKC": 25, "UTA": 26, "WAS": 27, "TOR": 28,
           "MEM": 29, "CHA": 30}
FROM_ESPN = {v: ABBR_TO_ID[k] for k, v in ESPN_ID.items()}
TEAM_NAMES = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "New Orleans Pelicans": "NOP", "Chicago Bulls": "CHI",
    "Cleveland Cavaliers": "CLE", "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND", "LA Clippers": "LAC",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Miami Heat": "MIA", "Milwaukee Bucks": "MIL",
    "Minnesota Timberwolves": "MIN", "Brooklyn Nets": "BKN", "New York Knicks": "NYK", "Orlando Magic": "ORL",
    "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX", "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC",
    "San Antonio Spurs": "SAS", "Oklahoma City Thunder": "OKC", "Utah Jazz": "UTA", "Washington Wizards": "WAS",
    "Toronto Raptors": "TOR", "Memphis Grizzlies": "MEM", "Charlotte Hornets": "CHA"}
KINDS = {1: "Preseason", 2: "Regular season", 3: "Playoffs", 5: "Play-In"}
POS = r"(?:PG|SG|SF|PF|C|G|F|G-F|F-G|F-C|C-F)"


def _get(url, params=None):
    time.sleep(config.SLEEP)
    return get_json(url, params=params, headers=HDR, retries=config.RETRIES, timeout=config.TIMEOUT)


# ------------------------------------------------------------------ schedule
def parse_events(data: dict, include_preseason=False) -> list[dict]:
    out = []
    for e in data.get("events", []):
        comp = e["competitions"][0]
        kind = e.get("season", {}).get("type", 2)
        if kind == 1 and not include_preseason:
            continue
        sides = {c["homeAway"]: c for c in comp["competitors"]}
        try:
            home = FROM_ESPN[int(sides["home"]["team"]["id"])]
            away = FROM_ESPN[int(sides["away"]["team"]["id"])]
        except (KeyError, ValueError):
            continue  # All-Star / international exhibition teams
        tip = datetime.fromisoformat(e["date"].replace("Z", "+00:00")).astimezone(ZoneInfo("UTC"))
        local = tip.astimezone(ET)
        venue = comp.get("venue", {})
        addr = venue.get("address", {})
        out.append({"game_id": str(e["id"]), "kind": KINDS.get(kind, "Other"), "date": local.date().isoformat(),
                    "tip_utc": tip.isoformat(), "tip_local": local.strftime("%-I:%M %p ET"),
                    "home_id": home, "away_id": away,
                    "home_name": sides["home"]["team"]["displayName"], "away_name": sides["away"]["team"]["displayName"],
                    "arena": venue.get("fullName", ""), "arena_city": addr.get("city") or TEAMS[home][1],
                    "arena_state": addr.get("state") or addr.get("country") or ""})
    return out


def fetch_games(day: date, include_preseason=False) -> list[dict]:
    data = _get(f"{SITE}/scoreboard", {"dates": day.strftime("%Y%m%d")})
    return [g for g in parse_events(data, include_preseason) if g["date"] == day.isoformat()]


def pick_slate(target: date | None, include_preseason=False, warnings: list | None = None):
    """Return (slate_date, games): `target` (default today ET) if it has games, else the next day that does."""
    start = target or datetime.now(ET).date()
    for offset in range(15):
        day = start + timedelta(days=offset)
        games = fetch_games(day, include_preseason)
        if games:
            if offset and warnings is not None:
                warnings.append(f"No games on {start}; showing next game day {day}")
            return day, games
    return start, []


# ------------------------------------------------------------------- rosters
def parse_roster(data: dict) -> list[dict]:
    athletes = []
    for a in data.get("athletes", []):
        athletes.extend(a["items"] if isinstance(a, dict) and "items" in a else [a])
    out = []
    for a in athletes:
        dob = (a.get("dateOfBirth") or "")[:10]
        try:
            birth = date.fromisoformat(dob) if dob else None
        except ValueError:
            birth = None
        bp = a.get("birthPlace") or {}
        out.append({"player_id": int(a["id"]), "name": a.get("fullName") or a.get("displayName"),
                    "birth_date": birth, "birth_city": bp.get("city") or "", "birth_state": bp.get("state") or "",
                    "birth_country": bp.get("country") or "", "school": (a.get("college") or {}).get("name", ""),
                    "position": (a.get("position") or {}).get("abbreviation", ""),
                    "jersey": str(a.get("jersey") or "")})
    return out


def roster(team_id_: int, season: str = "") -> list[dict]:
    return parse_roster(_get(f"{SITE}/teams/{ESPN_ID[abbr(team_id_)]}/roster"))


# -------------------------------------------------------------------- careers
def parse_career(data: dict, season: str):
    """Returns (rows, season_avg). rows: [{SEASON_ID, TEAM_ID, TEAM_ABBREVIATION, GP}] oldest first."""
    teams = {t["id"]: t for t in data.get("teams", {}).values()}
    cat = next((c for c in data.get("categories", []) if c.get("name") == "averages"), None)
    if not cat:
        return [], None
    labels = cat["labels"]
    rows, avg = [], None
    for r in cat.get("statistics", []):
        if "teamId" not in r or "season" not in r:
            continue
        t = teams.get(str(r["teamId"]))
        tid = team_id(t["abbreviation"]) if t else None
        if not tid:
            continue
        vals = dict(zip(labels, r["stats"]))
        rows.append({"SEASON_ID": r["season"]["displayName"], "TEAM_ID": tid, "TEAM_ABBREVIATION": abbr(tid),
                     "GP": int(float(vals.get("GP") or 0))})
        if r["season"]["displayName"] == season:
            f = lambda k: float(vals.get(k) or 0)  # noqa: E731
            avg = {"gp": int(f("GP")), "min": round(f("MIN"), 1), "pts": round(f("PTS"), 1),
                   "reb": round(f("REB"), 1), "ast": round(f("AST"), 1)}
    return rows, avg


def career(player_id: int, season: str):
    try:
        return parse_career(_get(f"{WEB}/athletes/{player_id}/stats"), season)
    except NotFound:
        return [], None  # rookies / new signings with no stats page yet: no history, not an error


# ------------------------------------------------------------------ game logs
def _local_date(ts) -> str:
    """ESPN game times are UTC; the game's calendar day is the Eastern one (an 8 PM ET tip is already tomorrow in UTC)."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(ET).date().isoformat()
    except (AttributeError, ValueError):
        return (ts or "")[:10]


def _venue(ev: dict) -> str:
    try:
        return abbr(FROM_ESPN[int(ev["homeTeamId"])])
    except (KeyError, ValueError, TypeError):
        return ""


def parse_gamelog(data: dict) -> list[dict]:
    """ESPN game log -> compact list (newest first) of regular season and playoff games."""
    names = data.get("names") or []
    events = data.get("events") or {}
    games = []
    for st in data.get("seasonTypes", []):
        label = st.get("displayName", "")
        if "Regular" not in label and "Postseason" not in label:
            continue
        for cat in st.get("categories", []):
            for row in cat.get("events", []):
                ev = events.get(str(row.get("eventId")))
                if not ev:
                    continue
                s = dict(zip(names, row.get("stats", [])))
                opp = team_id((ev.get("opponent") or {}).get("abbreviation"))
                if not opp:
                    continue

                def num(k):
                    try:
                        return float(s.get(k) or 0)
                    except ValueError:
                        return 0.0
                games.append({"gid": str(row.get("eventId")), "date": _local_date(ev.get("gameDate")),
                              "venue": _venue(ev), "opp": abbr(opp),
                              "home": ev.get("atVs") == "vs", "result": ev.get("gameResult", ""),
                              "score": ev.get("score", ""), "min": round(num("minutes")), "pts": round(num("points")),
                              "reb": round(num("totalRebounds")), "ast": round(num("assists")),
                              "playoff": "Postseason" in label})
    games.sort(key=lambda g: g["date"], reverse=True)
    return games


def gamelog(player_id: int, end_year: int) -> list[dict]:
    try:
        return parse_gamelog(_get(f"{WEB}/athletes/{player_id}/gamelog", {"season": end_year}))
    except NotFound:
        return []


# --------------------------------------------------------------------- trades
def parse_waive(desc: str):
    """'Waived G Dwight Murray Jr. and G Isaiah Wong.' -> [names]"""
    m = re.match(r"Waived (.+)", desc.strip())
    if not m:
        return None
    names = []
    for part in re.split(r",\s*| and ", m.group(1).rstrip(".")):
        pm = re.match(rf"^{POS}\s+(.+)$", part.strip())
        if pm:
            names.append(pm.group(1).strip().rstrip("."))
    return names or None
def parse_trade(desc: str):
    """'Acquired G Rob Dillingham from Chicago Bulls for G Buddy Hield.' -> ([names], from_team_id)"""
    m = re.match(r"Acquired (.+?) from ([A-Za-z0-9.' ]+?)(?: for | in exchange|\.|,| and |$)", desc.strip())
    if not m or m.group(2).strip() not in TEAM_NAMES:
        return None
    names = []
    for part in re.split(r",\s*| and ", m.group(1)):
        pm = re.match(rf"^{POS}\s+(.+)$", part.strip())
        if pm:
            names.append(pm.group(1).strip())
    return (names, ESPN_ID_TO_NBA(TEAM_NAMES[m.group(2).strip()])) if names else None


def ESPN_ID_TO_NBA(abbr_):  # noqa: N802
    return ABBR_TO_ID[abbr_]


def fetch_moves() -> list[dict]:
    """Recent trades and waivers from ESPN's transactions feed (it only covers roughly the last 10 months)."""
    data = _get(f"{SITE}/transactions", {"limit": 1000})
    out = []
    for t in data.get("transactions", []):
        desc = t.get("description", "")
        team = team_id(t["team"]["abbreviation"])
        parsed = parse_trade(desc)
        if parsed:
            for name in parsed[0]:
                out.append({"date": t["date"][:10], "player_name": norm_name(name), "from_team_id": parsed[1],
                            "to_team_id": team, "type": "trade"})
            continue
        waived = parse_waive(desc)
        if waived:
            for name in waived:
                out.append({"date": t["date"][:10], "player_name": norm_name(name), "from_team_id": team,
                            "to_team_id": None, "type": "waive"})
    return out
