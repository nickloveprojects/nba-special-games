"""NFL slate builder. Same flags as the NBA board (Revenge, Hometown, Birthday, Holiday, History) for quarterbacks,
running backs, receivers, tight ends and kickers, plus matchup grades from this season's real box scores.
Everything shown comes from ESPN data; anything we cannot confirm is labelled as unconfirmed."""
import json
import logging
import math
import re
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

from . import career, config, nfl_feed as feed, projection, weather
from .matchups import _color, _letter, _ordinal
from .net import SourceError
from .sources import geocode, media

log = logging.getLogger("nba")
OUT = config.OUT / "nfl"
IMG_DIR = config.IMG / "nfl"
RIVALRIES = config.ROOT / "config" / "rivalries_nfl.yaml"
MIN_GAMES_REVENGE = 6
WHO = {"QB": "quarterbacks", "RB": "running backs", "WR": "receivers", "TE": "tight ends"}
# stat -> (label, how to read it from one team's box-score group totals)
MATCHUP = {"QB": [("pass_yds", "PASS YDS", "passing yards"), ("pass_td", "PASS TD", "passing touchdowns")],
           "RB": [("rush_yds", "RUSH YDS", "rushing yards"), ("rec_yds", "REC YDS", "receiving yards")],
           "WR": [("rec_yds", "REC YDS", "receiving yards"), ("rec", "REC", "catches")],
           "TE": [("rec_yds", "REC YDS", "receiving yards"), ("rec", "REC", "catches")]}
EXPORT_URL = "https://www.espn.com/nfl/transactions"
EXITS = config.ROOT / "config" / "exits_nfl.yaml"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class Warn:
    def __init__(self):
        self.items = []

    def add(self, key, msg):
        if msg not in self.items:
            self.items.append(msg)


def _miles(a, b) -> float:
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 3959 * 2 * math.asin(math.sqrt(h))


def _f(x: float) -> str:
    return str(int(x)) if abs(x - round(x)) < 1e-9 else f"{x:.1f}"


def _times(n: int) -> str:
    return "1 time" if n == 1 else f"{n} times"


def _avg(rows: list[dict], key: str) -> float:
    return round(sum(r["row"].get(key, 0) for r in rows) / len(rows), 1) if rows else 0.0


def pretty_date(d: str) -> str:
    y, m, dd = d.split("-")
    return f"{MONTHS[int(m) - 1]} {int(dd)}, {y}"


# ------------------------------------------------------------------ stat lines by position
def summary(pos: str, rows: list[dict]) -> str:
    a = lambda k: _f(_avg(rows, k))  # noqa: E731
    if pos == "QB":
        return f"avg {a('passingYards')} pass yds, {a('passingTouchdowns')} TD, {a('interceptions')} INT"
    if pos == "RB":
        td = round(_avg(rows, "rushingTouchdowns") + _avg(rows, "receivingTouchdowns"), 1)
        return f"avg {a('rushingYards')} rush yds, {_f(td)} TD, {a('receptions')} rec"
    if pos in ("WR", "TE"):
        return f"avg {a('receptions')} rec, {a('receivingYards')} yds, {a('receivingTouchdowns')} TD"
    return f"avg {a('fieldGoalsMade-fieldGoalAttempts.made')} FG, {a('extraPointsMade-extraPointAttempts.made')} XP"


COLS = {"QB": ["C/ATT", "YDS", "TD", "INT", "RUSH"], "RB": ["ATT", "YDS", "TD", "REC", "REC YDS"],
        "WR": ["REC", "TGT", "YDS", "TD"], "TE": ["REC", "TGT", "YDS", "TD"], "K": ["FG", "XP"]}


def cells(pos: str, r: dict) -> list[str]:
    g = lambda k: _f(r.get(k, 0))  # noqa: E731
    if pos == "QB":
        return [f"{g('completions')}/{g('passingAttempts')}", g("passingYards"), g("passingTouchdowns"), g("interceptions"), g("rushingYards")]
    if pos == "RB":
        return [g("rushingAttempts"), g("rushingYards"), _f(r.get("rushingTouchdowns", 0) + r.get("receivingTouchdowns", 0)),
                g("receptions"), g("receivingYards")]
    if pos in ("WR", "TE"):
        return [g("receptions"), g("receivingTargets"), g("receivingYards"), g("receivingTouchdowns")]
    return [f"{g('fieldGoalsMade-fieldGoalAttempts.made')}/{g('fieldGoalsMade-fieldGoalAttempts.att')}",
            f"{g('extraPointsMade-extraPointAttempts.made')}/{g('extraPointsMade-extraPointAttempts.att')}"]


def game_rows(pos: str, logs: list[dict]) -> list[dict]:
    return [{"date": g["date"], "home": g["home"], "opp": g["opp"], "result": g["result"], "cells": cells(pos, g["row"])}
            for g in reversed(logs)]


# ------------------------------------------------------------------ matchup grades
def box_groups(box: dict, posmap: dict) -> dict:
    """One game's box score -> {TEAM: {QB/RB/WR/TE: totals}} of what each offense produced by position."""
    out = {}
    for team, ppl in box.items():
        g = {p: {"pass_yds": 0.0, "pass_td": 0.0, "rush_yds": 0.0, "rec_yds": 0.0, "rec": 0.0} for p in ("QB", "RB", "WR", "TE")}
        for pid, row in ppl.items():
            pos = posmap.get(int(pid))
            if pos not in g:
                continue
            n = lambda k: feed._num(row.get(k, 0))  # noqa: E731
            if pos == "QB":
                g[pos]["pass_yds"] += n("passing.passingYards")
                g[pos]["pass_td"] += n("passing.passingTouchdowns")
            g[pos]["rush_yds"] += n("rushing.rushingYards")
            g[pos]["rec_yds"] += n("receiving.receivingYards")
            g[pos]["rec"] += n("receiving.receptions")
        out[team] = g
    if len(out) == 2:
        a, b = list(out)
        out[a]["opp"], out[b]["opp"] = b, a
        return out
    return {}


def build_table(groups: list[dict]) -> dict:
    tot = {}
    for gm in groups:
        for team, g in gm.items():
            t = tot.setdefault(g["opp"], {"n": 0, **{p: {} for p in WHO}})
            t["n"] += 1
            for pos in WHO:
                for k, v in g[pos].items():
                    t[pos][k] = t[pos].get(k, 0) + v
    return {team: {"n": t["n"], **{p: {k: round(v / t["n"], 1) for k, v in t[p].items()} for p in WHO}} for team, t in tot.items() if t["n"]}


def matchup(table: dict, opp: str, pos: str) -> dict | None:
    if pos not in MATCHUP or opp not in table:
        return None
    teams = list(table)
    stats, pcts, labels = {}, {}, {}
    for key, label, _name in MATCHUP[pos]:
        vals = sorted((table[t][pos][key] for t in teams), reverse=True)
        v = table[opp][pos][key]
        rank = vals.index(v) + 1
        pct = 1 - (rank - 1) / (len(teams) - 1) if len(teams) > 1 else 0.5
        stats[key] = {"value": v, "rank": rank, "of": len(teams), "color": _color(pct)}
        pcts[key], labels[key] = pct, label
    score = round(sum(pcts.values()) / len(pcts) * 100)
    best = max(pcts, key=lambda k: pcts[k])
    name = next(n for k, _l, n in MATCHUP[pos] if k == best)
    b = stats[best]
    return {"group": pos, "games": table[opp]["n"], "stats": stats, "labels": labels, "score": score,
            "grade": _letter(score), "color": _color(score / 100), "best": best,
            "note": f"{opp} gives up the {_ordinal(b['rank'])}-most {name} to {WHO[pos]} ({_f(b['value'])} a game, {table[opp]['n']} games)."}


def load_table(conn, week: int, posmap: dict, warn) -> dict:
    groups = []
    for gid in feed.finished_games(week):
        try:
            g = box_groups(feed.box_for_game(conn, gid), posmap)
        except SourceError as e:
            warn.add("box", f"Some box scores were unavailable ({e})")
            continue
        if g:
            groups.append(g)
    return build_table(groups)


# ------------------------------------------------------------------ flags
def load_rivalries(warn) -> list[dict]:
    if not RIVALRIES.exists():
        return []
    try:
        return (yaml.safe_load(RIVALRIES.read_text()) or {}).get("rivalries") or []
    except yaml.YAMLError as e:
        warn.add("rivalries", f"rivalries_nfl.yaml could not be read ({e})")
        return []


def stint(logs: list[dict], team_id: int) -> tuple[int, int, int] | None:
    rows = [g for g in logs if g["team_id"] == team_id]
    return (len(rows), rows[0]["season"], rows[-1]["season"]) if rows else None


AMBIGUOUS_PLACE = {"New York", "Los Angeles"}
HEAD = {"trade": "Traded by the {t}.", "waived": "Released by the {t}.", "free_agency": "Left the {t} in free agency."}
POS_CODE = r"(?:QB|RB|WR|TE|FB|PK|LS|[A-Z]{1,3}s?)"


def clip(sent: str, name: str) -> str:
    """ESPN packs several players into one sentence. Keep only the part about this player (never reword it)."""
    verb = sent.split()[0]
    pos = re.search(r"\b(" + POS_CODE + r")\s+" + re.escape(name), sent)
    others = len(re.findall(r"\b[A-Z]{1,3}s?\s+[A-Z][a-zA-Z'.\-]+ [A-Z]", sent)) > 1
    if pos and (others or len(sent) > 220) and verb in ("Released", "Waived", "Signed", "Re-signed", "Claimed"):
        return f"{verb} {pos.group(1)} {name}."
    return sent if len(sent) <= 260 else sent[:257] + "..."


def exit_for(p, left, logs, rows_for_year, t_all, today_iso):
    """How the player left `left` (a team dict), from ESPN's transaction log between his last game for that team and his
    first game for the next one. Returns {kind: trade|waived|signed_elsewhere, date, text, new} or None.
    Only trades and releases are treated as confirmed; a later signing elsewhere is reported as a fact, not as a reason."""
    idx = [i for i, g in enumerate(logs) if g["team_id"] == left["id"]]
    if not idx:
        return None
    i = idx[-1]
    nxt = next((g for g in logs[i + 1:] if g["team_id"] != left["id"] and g["team_id"] in t_all), None)
    start, end = logs[i]["date"], (nxt["date"] if nxt else today_iso)
    new = t_all.get(nxt["team_id"]) if nxt else None
    place = left["name"].rsplit(" ", 1)[0]
    name = p["name"]
    firm, later = [], []
    for y in range(int(start[:4]), int(end[:4]) + 1):
        for r in rows_for_year(y):
            if not (start <= r["date"] <= end) or name not in r["text"]:
                continue
            for sent in feed._sentences(r["text"]):
                if name not in sent:
                    continue
                other = r["team"] != left["abbr"]
                if not other and re.match(r"(Traded|Waived|Released?|Terminated)\b", sent) and "in exchange for" not in sent.split(name)[0]:
                    firm.append(("trade" if sent.startswith("Traded") else "waived", r["date"], sent))
                elif other and re.match(r"(Acquired|Claimed|Received)\b", sent) and " from " in sent:
                    frm = sent.split(" from ", 1)[1]
                    if left["short"] in frm or left["name"] in frm or (place in frm and place not in AMBIGUOUS_PLACE):
                        firm.append(("waived" if sent.startswith("Claimed") else "trade", r["date"], sent))
                elif other and new and r["team"] == new["abbr"] and sent.startswith("Traded") and "in exchange for" in sent \
                        and name in sent.split("in exchange for", 1)[1]:
                    firm.append(("trade_new_side", r["date"], sent))      # the new club's side of a trade for him
                elif other and sent.startswith("Signed") and (new is None or r["team"] == new["abbr"]):
                    later.append(("signed_elsewhere", r["date"], sent))
    pick = max(firm, key=lambda x: (x[0] != "trade_new_side", x[1])) if firm else (min(later, key=lambda x: x[1]) if later else None)
    if not pick:
        return None
    return {"kind": pick[0], "date": pick[1], "text": clip(pick[2], name), "new": new["short"] if new else ""}


def load_exits(warn=None) -> dict:
    """Researched, sourced exits from config/exits_nfl.yaml, keyed by (player name, former team abbreviation)."""
    try:
        rows = (yaml.safe_load(EXITS.read_text()) or {}).get("exits") or [] if EXITS.exists() else []
    except yaml.YAMLError as e:
        if warn:
            warn.add("exits", f"exits_nfl.yaml could not be read ({e})")
        return {}
    return {(r["player"], r["from_team"]): r for r in rows
            if r.get("player") and r.get("from_team") and r.get("kind") in HEAD and r.get("how") and r.get("sources")}


def revenge_tag(p, opp_info, logs, rows_for_year, t_all, today_iso, curated=None):
    s = stint(logs, opp_info["id"])
    if not s or s[0] < MIN_GAMES_REVENGE:
        return None
    n, first, last = s
    span = f"in {first}" if first == last else f"from {first} to {last}"
    played = f"Played for the {opp_info['short']} {span} ({n} games)."
    cur = (curated or {}).get((p["name"], opp_info["abbr"]))
    if cur:
        kind = cur["kind"]
        return {"category": "Revenge", "kind": kind, "confidence": "high", "headline": HEAD[kind].format(t=opp_info["short"]),
                "detail": played, "how_left": cur["how"], "sources": cur["sources"],
                "_score": {"trade": 5, "waived": 4, "free_agency": 3}[kind]}
    ex = exit_for(p, opp_info, logs, rows_for_year, t_all, today_iso)
    src = []
    if ex and ex["kind"] in {"trade", "waived", "trade_new_side"}:
        kind, conf = ("trade" if ex["kind"] == "trade_new_side" else ex["kind"]), "high"
        how = f"{ex['text']} ({pretty_date(ex['date'])})"
        if ex["kind"] == "trade_new_side":
            how = f"Traded to the {ex['new']}. ESPN's log: {how}"
        src = [{"label": "ESPN transactions", "url": EXPORT_URL}]
        head = HEAD[kind].format(t=opp_info["short"])
    else:
        kind, conf = "unknown", "low"
        nxt = f" His next signing was with the {ex['new']} ({pretty_date(ex['date'])})." if ex and ex["new"] else ""
        how = f"{played} No trade or release is in ESPN's log, so how he left is not confirmed.{nxt}"
        head = f"Former {opp_info['short']} player."
    return {"category": "Revenge", "kind": kind, "confidence": conf, "headline": head, "detail": played,
            "how_left": how, "sources": src, "_score": {"trade": 5, "waived": 4}.get(kind, 2)}


def birthday_tag(p, logs, d: date):
    mine = [g for g in logs if g["date"][5:] == f"{d.month:02d}-{d.day:02d}" and not (g["date"] == d.isoformat())]
    detail = f"Turns {d.year - int(p['dob'][:4])} today." if p["dob"] else "Birthday."
    tag = {"category": "Birthday", "kind": "birthday", "confidence": "high", "headline": "Birthday game.", "detail": detail, "sources": [], "_score": 1}
    return tag, mine


def hometown_tag(conn, p, venue_abbr, warn):
    """Born within HOMETOWN_RADIUS_MI of tonight's stadium. States far from the stadium are skipped before any lookup."""
    if not (p["city"] and venue_abbr in feed.VENUE):
        return None
    v = feed.VENUE[venue_abbr]
    c = feed.STATE_CENTER.get(p["state"])
    if c and _miles(c, v) > 350:
        return None
    try:
        place = geocode.get_place(conn, p["city"], p["state"], p["country"])
    except SourceError as e:
        warn.add("geocode", f"Some birthplaces could not be located ({e})")
        return None
    if not place:
        return None
    d = _miles((place["lat"], place["lon"]), v)
    if d > config.HOMETOWN_RADIUS_MI:
        return None
    return {"category": "Hometown", "kind": "birthplace", "confidence": "high", "headline": "Hometown game.",
            "detail": f"Born in {p['city']}, {p['state'] or p['country']}, about {round(d)} {'mile' if round(d) == 1 else 'miles'} from the stadium.",
            "sources": [{"label": "Wikidata", "url": place["source_url"]}], "_score": 3, "_place": (place["lat"], place["lon"])}


def career_lines(p, logs, tags, opp, opp_name, d: date, id_abbr, hometown_xy):
    pos, out = p["pos"], []
    sc = f"since {logs[0]['season']}" if logs else ""

    def line(label, rows, noun):
        out.append({"label": label, "text": f" {noun}: {_times(len(rows))} ({summary(pos, rows)}).", "scope": sc})

    cats = {t["category"] for t in tags}
    if "Birthday" in cats and p["dob"]:
        mine = [g for g in logs if g["date"][5:] == p["dob"][5:] and g["date"] != d.isoformat()]
        if mine:
            line("Birthday games", mine, "On his birthday")
    if "Hometown" in cats and hometown_xy:
        mine = [g for g in logs if g["date"] != d.isoformat() and (id_abbr.get(g["home_id"]) in feed.VENUE)
                and _miles(feed.VENUE[id_abbr[g["home_id"]]], hometown_xy) <= config.HOMETOWN_RADIUS_MI]
        if mine:
            line("Hometown games", mine, "In his hometown area")
    if "Holiday" in cats:
        hol = career.holiday_name(d)
        mine = [g for g in logs if g["date"] != d.isoformat() and career.holiday_name(date.fromisoformat(g["date"])) == hol]
        if mine:
            line(f"{hol} games", mine, f"On {hol}")
    return out


def holiday_tag(p, logs, d: date, opp, opp_name):
    name = career.holiday_name(d)
    past = [g for g in logs if g["date"] != d.isoformat() and career.holiday_name(date.fromisoformat(g["date"])) == name]
    if not name or not past:
        return None
    lines = [{"text": f"Has played on {name} {_times(len(past))} ({summary(p['pos'], past)})."}]
    vs = [g for g in logs if g["opp"] == opp and g["date"] != d.isoformat()]
    if vs:
        lines.append({"text": f"Has faced the {opp_name} {_times(len(vs))} in his career ({summary(p['pos'], vs)})."})
    both = [g for g in past if g["opp"] == opp]
    if both:
        lines.append({"text": f"On {name} against the {opp_name}: {_times(len(both))} ({summary(p['pos'], both)})."})
    return {"category": "Holiday", "kind": "holiday", "label": name, "confidence": "high", "headline": f"{name} game.",
            "detail": lines[0]["text"], "lines": lines, "sources": [], "_score": 2}


def history_tags(p, opp_ids, rivalries, roster_names):
    out = []
    for r in rivalries:
        a, b = r.get("players", [None, None])
        if not (r.get("reason") and r.get("sources")):
            continue
        other = b if p["name"] == a else a if p["name"] == b else None
        if other and other in roster_names:
            out.append({"category": "History", "kind": "rivalry", "label": r.get("kind", "Rivalry"), "with": other,
                        "confidence": "high", "headline": f"{r.get('kind', 'Rivalry')} with {other}.", "reason": r["reason"],
                        "detail": r["reason"], "sources": r["sources"], "_score": 3})
    return out


# ------------------------------------------------------------------ build
def recent_block(p, logs, opp):
    cur = logs[-5:]
    vs = [g for g in logs if g["opp"] == opp][-5:]
    pos = p["pos"]
    return {"cols": COLS[pos],
            "form": {"n": len(cur), "text": summary(pos, cur) if cur else "", "games": game_rows(pos, cur)},
            "vs": {"opp": opp, "n": len(vs), "text": summary(pos, vs) if vs else "", "games": game_rows(pos, vs),
                   "note": f"No games vs {opp} in the last 8 seasons."}}


def _summary(t: dict, opp: str) -> str:
    if t["category"] == "Revenge":
        return {"trade": f"Faces the {opp}, who traded him.", "waived": f"Faces the {opp}, who released him.",
                "free_agency": f"Faces the {opp}, his former team."}.get(t["kind"], f"Faces the {opp}, his former team.")
    return t.get("headline") or t.get("detail") or ""


def build_slates(today: date | None = None) -> list[dict]:
    warn = Warn()
    conn = feed.connect()
    year, week, events = feed.current_week_events()
    t_all = feed.teams()
    abbr_id = {t["abbr"]: i for i, t in t_all.items()}
    id_abbr = {i: t["abbr"] for i, t in t_all.items()}
    today = today or datetime.now(feed.ET).date()
    days = sorted({e["date"] for e in events if e["date"] >= today.isoformat()}) or sorted({e["date"] for e in events})
    log.info("NFL week %s: %s games on %s", week, len(events), days)

    rosters = {}
    for tid in t_all:
        try:
            rosters[tid] = feed.roster(conn, tid)
        except SourceError as e:
            warn.add("roster", f"Roster unavailable for {t_all[tid]['abbr']} ({e})")
    posmap = {p["id"]: p["pos"] for r in rosters.values() for p in r}
    table = load_table(conn, week, posmap, warn)
    cur_year = today.year
    tx_seen = {}

    def rows_for_year(y):
        if y not in tx_seen:
            try:
                tx_seen[y] = feed.transactions_year(conn, y, cur_year)
            except SourceError as e:
                warn.add("tx", f"ESPN transactions for {y} unavailable, so some exits show as unconfirmed ({e})")
                tx_seen[y] = []
        return tx_seen[y]
    rivalries = load_rivalries(warn)
    curated = load_exits(warn)
    needs = []
    geocode.reset()
    slates = []
    for day in days:
        d = date.fromisoformat(day)
        day_events = [e for e in events if e["date"] == day]
        prior = _prior_projections(day)
        wx = weather.forecast_many([
            {"id": e["game_id"], "lat": xy[0], "lon": xy[1], "tip_utc": e["tip_utc"], "indoor": e["indoor"]}
            for e in day_events if not e["neutral"] and (xy := feed.VENUE.get(id_abbr[int(e["home"]["id"])]))])
        wx = {e["game_id"]: wx.get(e["game_id"]) for e in day_events}
        entries = []
        for e in day_events:
            for side, other in (("home", "away"), ("away", "home")):
                me, opp = e[side], e[other]
                tid, oid = int(me["id"]), int(opp["id"])
                mi, oi = t_all[tid], t_all[oid]
                roster_names = {p["name"] for p in rosters.get(oid, [])}
                for p in rosters.get(tid, []):
                    tags, tx_logs = [], None
                    # cheap flags first (no extra requests)
                    if p["dob"] and p["dob"][5:] == day[5:]:
                        tags.append(birthday_tag(p, [], d)[0])
                    hxy = None
                    if not e["neutral"]:
                        ht = hometown_tag(conn, p, mi["abbr"] if side == "home" else oi["abbr"], warn)
                        if ht:
                            hxy = ht.pop("_place")
                            tags.append(ht)
                    hist = history_tags(p, {oid}, rivalries, roster_names)
                    tags += hist
                    hol = career.holiday_name(d)
                    revenge_cand = p["years"] > 0 and oid in feed.past_teams(conn, p["id"]) and oid != tid
                    if not (tags or hol or revenge_cand):
                        continue
                    try:
                        logs = feed.career_logs(conn, p["id"], p["years"], year)
                    except SourceError as ex:
                        warn.add("gamelog", f"Game log unavailable for {p['name']} ({ex})")
                        continue
                    if revenge_cand:
                        rv = revenge_tag(p, oi, logs, rows_for_year, t_all, day, curated)
                        if rv:
                            tags.append(rv)
                            if rv["kind"] == "unknown":
                                needs.append(f"{p['name']} ({mi['abbr']}) left {oi['abbr']} [{oi['id']}]")
                    if hol:
                        ht = holiday_tag(p, logs, d, oi["abbr"], oi["short"])
                        if ht:
                            tags.append(ht)
                    if not tags:
                        continue
                    tags.sort(key=lambda t: -t["_score"])
                    entry = {
                        "player_id": p["id"], "name": p["name"], "team": mi["abbr"], "team_name": mi["short"],
                        "team_color": mi["color"], "team_alt": mi["alt"], "opponent": oi["abbr"], "opponent_name": oi["short"],
                        "opponent_color": oi["color"], "position": p["pos"], "jersey": p["jersey"], "home_away": side,
                        "game_id": e["game_id"], "game_kind": e["kind"], "tip": e["tip"], "tip_utc": e["tip_utc"],
                        "weather": wx[e["game_id"]], "weather_text": weather.label(wx[e["game_id"]]), "arena": e["arena"], "location": ", ".join(x for x in (e["venue_city"], e["venue_state"]) if x),
                        "categories": sorted({t["category"] for t in tags}, key=["Revenge", "Hometown", "Birthday", "Holiday", "History"].index),
                        "summary": _summary(tags[0], oi["short"]),
                        "score": float(sum(t["_score"] for t in tags)), "stats": {},
                        "status_note": p["injury"], "espn_url": f"https://www.espn.com/nfl/player/_/id/{p['id']}",
                        "recent": recent_block(p, logs, oi["abbr"]), "matchup": matchup(table, oi["abbr"], p["pos"]),
                        "career": career_lines(p, logs, tags, oi["abbr"], oi["short"], d, id_abbr, hxy),
                        "projection": projection.freeze(
                            None if projection.started(e["tip_utc"]) else projection.project(
                                p["pos"], logs, table, oi["abbr"], today, p["id"] * 100003 + int(e["game_id"]), p["injury"],
                                weather=weather.passing_factor(wx[e["game_id"]])),
                            prior.get(p["id"]), e["tip_utc"]),
                        "_headshot": p["headshot"], "tags": tags}
                    for t in tags:
                        t.pop("_score", None)
                    entries.append(entry)
        entries.sort(key=lambda x: (-x["score"], x["name"]))
        for x in entries:
            sh = x.pop("_headshot")
            ok = bool(sh) and media._save(sh, IMG_DIR / "players" / f"{x['player_id']}.png")
            x["headshot"] = f"img/nfl/players/{x['player_id']}.png" if ok else None
            for k, a in (("team_logo", x["team"]), ("opponent_logo", x["opponent"])):
                x[k] = _logo(a)
        matchups = [{"away": id_abbr[int(e["away"]["id"])], "home": id_abbr[int(e["home"]["id"])], "tip": e["tip"],
                     "away_logo": _logo(id_abbr[int(e["away"]["id"])]), "home_logo": _logo(id_abbr[int(e["home"]["id"])])}
                    for e in day_events]
        slates.append({"date": day, "sport": "nfl", "week": week, "games": len(day_events), "entries": entries,
                       "matchups": matchups, "warnings": warn.items,
                       "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
    if needs:
        log.info("NEEDS RESEARCH (exit not confirmed): %s", "; ".join(sorted(set(needs))))
    return slates


def _prior_projections(day: str) -> dict:
    """Projections already published for this day, by player id, so they can be kept once the game starts."""
    f = OUT / f"{day}.json"
    try:
        return {x["player_id"]: x["projection"] for x in json.loads(f.read_text()).get("entries", []) if x.get("projection")}
    except (OSError, ValueError, KeyError):
        return {}


def _logo(abbr: str) -> str | None:
    key = {"WSH": "wsh", "LV": "lv"}.get(abbr, abbr.lower())
    ok = media._save(f"{media.COMBINER}/i/teamlogos/nfl/500/{key}.png&w=96&h=96", IMG_DIR / "teams" / f"{abbr}.png")
    return f"img/nfl/teams/{abbr}.png" if ok else None


def write(slates: list[dict]):
    OUT.mkdir(parents=True, exist_ok=True)
    keep = []
    for s in slates:
        (OUT / f"{s['date']}.json").write_text(json.dumps(s, indent=1))
        keep.append(s["date"])
    for p in OUT.glob("????-??-??.json"):
        if p.stem not in keep:
            p.unlink()
    (OUT / "index.json").write_text(json.dumps({"dates": sorted(keep), "latest": sorted(keep)[0], "week": slates[0]["week"] if slates else None}))


def run(today: date | None = None) -> list[dict]:
    slates = build_slates(today)
    write(slates)
    return slates
