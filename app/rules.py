"""Pure, side-effect-free detection logic (fully unit-tested, no network)."""
import calendar
import difflib
import math
import re
import unicodedata
from datetime import date

from .teams_geo import team_id

SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


def norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z\s]", "", s.lower().replace("-", " "))
    return " ".join(t for t in s.split() if t not in SUFFIXES)


def name_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, norm_name(a), norm_name(b)).ratio()


def haversine_mi(lat1, lon1, lat2, lon2) -> float:
    r = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ----------------------------------------------------------------- birthday
def birthday_tag(birth: date | None, game_date: date) -> dict | None:
    if not birth:
        return None
    m, d, note = birth.month, birth.day, ""
    if (m, d) == (2, 29) and not calendar.isleap(game_date.year):
        d, note = 28, " (Feb 29 birthday, observed Feb 28)"
    if (game_date.month, game_date.day) != (m, d):
        return None
    age = game_date.year - birth.year
    return {"category": "Birthday", "kind": "birthday", "confidence": "high",
            "headline": f"Turns {age} today{note}.", "detail": f"Turns {age} today{note}", "sources": []}


# ----------------------------------------------------------------- hometown
def _near(place, loc, radius):
    if place.get("lat") is None or loc is None:
        return None
    return haversine_mi(place["lat"], place["lon"], loc[0], loc[1])


def hometown_tags(places: list[dict], game_loc, opp_loc, is_home: bool, arena_city: str, radius: float) -> list[dict]:
    """places: where the player is from, best first. Each is {kind: override|high_school|birthplace, label,
    lat, lon, school?, note?, source_url?}. Prefers where he grew up (override, then high school) over birthplace.
    Returns 0 or 1 tag."""
    if not places:
        return []

    def hit(pl):
        """(miles, 'here' | 'opponent') when this place is within the radius of the game or of the opposing city."""
        d_game, d_opp = _near(pl, game_loc, radius), _near(pl, opp_loc, radius)
        if d_game is not None and d_game <= radius:
            return d_game, "here"
        if is_home and d_opp is not None and d_opp <= radius:
            return d_opp, "opponent"
        if d_game is None and pl.get("label") and arena_city and arena_city.lower() in pl["label"].lower():
            return 0.0, "here"          # no coordinates: fall back to matching the city name
        return None

    def build(pl, where, miles, confidence, headline, detail):
        return {"category": "Hometown", "kind": pl["kind"], "confidence": confidence, "headline": headline,
                "detail": detail, "miles": round(miles), "where": where}

    for pl in places:
        if pl["kind"] == "override":
            h = hit(pl)
            if h:
                note = f" ({pl['note']})" if pl.get("note") else ""
                return [build(pl, h[1], h[0], "high",
                              "Plays in his hometown area." if h[1] == "here" else "Faces a team from his hometown area.",
                              f"Hometown set manually: {pl['label']}{note}")]
    hs = [pl for pl in places if pl["kind"] == "high_school"]
    birth = next((pl for pl in places if pl["kind"] == "birthplace"), None)
    for pl in hs:
        h = hit(pl)
        if h:
            born = f" Born in {birth['label']}." if birth else ""
            return [build(pl, h[1], h[0], "high",
                          "Plays near where he grew up." if h[1] == "here" else "Faces a team from where he grew up.",
                          f"Went to {pl['school']} in {pl['label']} (about {h[0]:.0f} mi away).{born}")]
    if birth:
        h = hit(birth)
        if h:
            known_hs = [pl for pl in hs if pl.get("lat") is not None]
            if known_hs:
                return []               # born here but raised somewhere else: not a hometown game
            why = "high school not found" if not hs else "high school location not found"
            return [build(birth, h[1], h[0], "low",
                          "Born near here; couldn't confirm he grew up here.",
                          f"Born in {birth['label']} ({why}).")]
    return []


# ------------------------------------------------------------------ revenge
def _start_year(season_id: str) -> int:
    return int(season_id[:4])


def build_stints(rows: list[dict]) -> dict[int, dict]:
    """rows: nba_api PlayerCareerStats season totals (chronological; a multi-team season has a
    TOT row followed by its team rows in chronological order).
    Returns {team_id: {abbr, first_season, last_season, gp, left_midseason, left_year}}."""
    by_season: dict[str, list[dict]] = {}
    for r in rows:
        by_season.setdefault(r["SEASON_ID"], []).append(r)
    stints: dict[int, dict] = {}
    for season, srows in by_season.items():
        teams = [r for r in srows if r["TEAM_ID"] not in (0, None) and r["TEAM_ABBREVIATION"] != "TOT"]
        for i, r in enumerate(teams):
            s = stints.setdefault(r["TEAM_ID"], {"abbr": r["TEAM_ABBREVIATION"], "first_season": season,
                                                 "last_season": season, "gp": 0,
                                                 "left_midseason": False, "left_year": None})
            s["gp"] += int(r.get("GP") or 0)
            if season >= s["last_season"]:
                s["last_season"] = season
                s["left_midseason"] = i < len(teams) - 1
                s["left_year"] = _start_year(season) + 1
            s["first_season"] = min(s["first_season"], season)
    return stints


def current_team_from_rows(rows: list[dict]) -> int | None:
    teams = [r["TEAM_ID"] for r in rows if r["TEAM_ID"] not in (0, None)]
    return teams[-1] if teams else None



def build_exits(txs: list[dict]) -> dict[int, dict]:
    """Walk a player's transaction log (oldest first) and record, per team, how he LAST left it.
    Returns {team_id: {kind: trade|waived|free_agency, date, to, text}}."""
    exits: dict[int, dict] = {}
    current = None
    for t in txs:
        ids = [i for i in (team_id(a) for a in t.get("teams", [])) if i]
        kind = t["kind"]
        if kind == "trade" and len(ids) >= 2:
            exits[ids[0]] = {"kind": "trade", "date": t["date"], "to": ids[1], "text": t["text"]}
            current = ids[1]
        elif kind == "waive" and ids:
            exits[ids[0]] = {"kind": "waived", "date": t["date"], "to": None, "text": t["text"]}
            current = None
        elif kind == "claim" and ids:
            if current and current != ids[0]:
                exits[current] = {"kind": "waived", "date": t["date"], "to": ids[0], "text": t["text"]}
            current = ids[0]
        elif kind in ("draft", "fa_sign", "sign") and ids:
            if kind != "draft" and current and current != ids[0]:
                exits[current] = {"kind": "free_agency", "date": t["date"], "to": ids[0], "text": t["text"]}
            current = ids[0]
    return exits


def pretty_date(iso: str) -> str:
    try:
        d = date.fromisoformat(iso)
        return f"{d.strftime('%b')} {d.day}, {d.year}"
    except ValueError:
        return iso


def trade_return(text: str, max_len: int = 130) -> str:
    """'Traded by X with cash to the Y for A and B. Y received a trade exception.' -> 'for A and B'"""
    i = text.find(" to the ")
    if i < 0:
        return ""
    rest = text[i + 8:]
    rest = re.split(r"\.\s+[A-Z][A-Za-z.' ]* (?:received|will receive)", rest)[0]
    rest = re.sub(r"\s*\([^)]*\)", "", rest).strip().rstrip(".")
    j = rest.find(" for ")
    if j < 0:
        return ""
    out = rest[j + 1:]
    return out if len(out) <= max_len else out[:max_len].rsplit(" ", 1)[0] + "..."


def how_left_text(ext: dict | None, to_nick: str | None) -> str:
    if not ext:
        return "How he left isn't confirmed yet."
    when = pretty_date(ext["date"])
    if ext["kind"] == "trade":
        ret = trade_return(ext["text"])
        dest = f" to the {to_nick}" if to_nick else ""
        return f"Traded{dest}{(' ' + ret) if ret else ''} ({when})."
    if ext["kind"] == "waived":
        buyout = ", with a buyout" if "buyout" in ext["text"].lower() else ""
        return f"Waived{buyout} ({when})."
    dest = f" with the {to_nick}" if to_nick else ""
    return f"Contract ended; signed{dest} as a free agent ({when})."


def revenge_tag(stint: dict | None, ext: dict | None, opp_nick: str, to_nick: str | None, manual_note: str | None,
                min_gp: int, this_year: int) -> dict | None:
    """Revenge / old-team tag, or None. `ext` is a confirmed exit record from the player's transaction log."""
    if not stint and not manual_note:
        return None
    kind = ext["kind"] if ext else "unknown"
    gp = stint["gp"] if stint else 0
    need = 5 if kind in ("trade", "waived") else min_gp
    if not manual_note and gp < need:
        return None                      # cup-of-coffee stints are noise
    conf = {"trade": "high", "waived": "high", "free_agency": "medium"}.get(kind, "low")
    if kind == "unknown" and stint and stint.get("left_midseason"):
        conf = "medium"                  # leaving mid-season almost always means a trade or waiver
    year = ext["date"][:4] if ext else (str(stint["left_year"]) if stint and stint.get("left_year") else "")
    if kind == "trade":
        headline = f"Faces the {opp_nick}, who traded him on {pretty_date(ext['date'])}."
    elif kind == "waived":
        headline = f"Faces the {opp_nick}, who waived him on {pretty_date(ext['date'])}."
    elif kind == "free_agency":
        headline = f"Faces his former team, the {opp_nick}. He left in free agency in {year}."
    else:
        span = ""
        if stint:
            span = (stint["first_season"] if stint["first_season"] == stint["last_season"]
                    else f"{stint['first_season']} to {stint['last_season']}")
        headline = f"Faces his former team, the {opp_nick}" + (f" ({span})." if span else ".")
    how = how_left_text(ext, to_nick)
    if manual_note:
        conf = "high"
        how = f"{how} {manual_note}".strip() if ext else manual_note
        headline = f"{headline} {manual_note}" if kind == "unknown" and not stint else headline
    games = f"{gp} games with the {opp_nick}" if stint else ""
    return {"category": "Revenge", "kind": kind, "confidence": conf, "headline": headline, "how_left": how,
            "detail": f"{headline} {how}".strip(), "games_with_team": games,
            "_score": revenge_score(stint, conf, this_year, ext)}


def revenge_score(stint, conf, this_year, ext=None) -> float:
    base = {"high": 3.0, "medium": 2.0, "low": 1.0}[conf]
    year = int(ext["date"][:4]) if ext else (stint or {}).get("left_year")
    if not year:
        return base
    recency = max(0, 5 - (this_year - year)) * 0.4
    return round(base + recency + min(((stint or {}).get("gp", 0)) / 200, 1), 2)


# ------------------------------------------------------------- recent games
def _avg(games, key):
    return round(sum(g[key] for g in games) / len(games), 1) if games else 0


def summarize_games(games: list[dict]) -> dict:
    return {"games": games, "n": len(games), "pts": _avg(games, "pts"), "reb": _avg(games, "reb"),
            "ast": _avg(games, "ast"), "min": _avg(games, "min")}


def recent_summary(all_games: list[dict], opp_abbr: str, form_n: int = 5, vs_n: int = 5) -> dict:
    """all_games newest first. Returns last `form_n` games and last `vs_n` against `opp_abbr`."""
    vs = [g for g in all_games if g["opp"] == opp_abbr][:vs_n]
    return {"form": summarize_games(all_games[:form_n]), "vs": {"opp": opp_abbr, **summarize_games(vs)}}


def _h2h_avg(rows: list[dict]) -> dict:
    n = len(rows)
    if not n:
        return {"n": 0}
    f = lambda k: round(sum(r[k] for r in rows) / n, 1)  # noqa: E731
    return {"n": n, "min": f("min"), "pts": f("pts"), "reb": f("reb"), "ast": f("ast")}


def head_to_head(log_a: list[dict], log_b: list[dict]) -> dict:
    """Games where BOTH players appeared in the same game (matched by ESPN game id).
    Returns each player's averages in those games and A's team record. Nothing is estimated."""
    ids_b = {g["gid"]: g for g in log_b if g.get("gid")}
    pairs = [(g, ids_b[g["gid"]]) for g in log_a if g.get("gid") in ids_b]
    pairs.sort(key=lambda p: p[0]["date"], reverse=True)
    a = [p[0] for p in pairs]
    w = sum(1 for g in a if g["result"] == "W")
    l = sum(1 for g in a if g["result"] == "L")
    return {"games": len(pairs), "a": _h2h_avg(a), "b": _h2h_avg([p[1] for p in pairs]), "a_record": f"{w}-{l}",
            "first": pairs[-1][0]["date"] if pairs else None, "last": pairs[0][0]["date"] if pairs else None,
            "recent": [{"date": x["date"], "a_pts": x["pts"], "b_pts": y["pts"], "a_result": x["result"],
                        "playoff": x["playoff"]} for x, y in pairs[:5]]}
