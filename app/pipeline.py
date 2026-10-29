"""Daily pipeline: schedule -> rosters -> (cached) bios, careers, high schools, transaction logs -> rules -> slate JSON.
Every external call is wrapped: failures become warnings and cached data is used where possible."""
import json
import logging
from datetime import date, datetime, timezone

import yaml

from . import career, config, db, matchups, nba_projection, output, projection, rules
from .net import SourceError
from .sources import bbref, espn, geocode, media, transactions
from .teams_geo import NICK, TEAMS, abbr, nick, team_id

log = logging.getLogger("nba")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


def load_overrides() -> dict:
    try:
        d = yaml.safe_load(config.OVERRIDES.read_text()) or {}
    except FileNotFoundError:
        d = {}

    def by_key(items):
        return {(it.get("player_id") or rules.norm_name(it.get("player", ""))): it for it in (items or [])}

    return {"hometown": by_key(d.get("hometown")), "revenge": d.get("revenge") or [],
            "ignore": {rules.norm_name(n) for n in (d.get("ignore_players") or [])}}


def _age_days(ts) -> float:
    if not ts:
        return 10 ** 6
    return (datetime.now(timezone.utc).replace(tzinfo=None) - datetime.fromisoformat(ts)).total_seconds() / 86400


class Warnings:
    """Collects warnings; repeated failures of one kind are summarised instead of flooding the list."""

    def __init__(self):
        self.items, self.counts = [], {}

    def add(self, kind, msg, keep=2):
        self.counts[kind] = self.counts.get(kind, 0) + 1
        if self.counts[kind] <= keep:
            self.items.append(msg)

    def finish(self, keep=2):
        for kind, n in self.counts.items():
            if n > keep:
                self.items.append(f"...and {n - keep} more '{kind}' problems (same cause is likely)")
        return sorted(set(self.items))


# ---------------------------------------------------------------- cached enrichers
def ensure_career(conn, p, season, warn):
    row = conn.execute("SELECT career_fetched, career_last_team FROM players WHERE player_id=?",
                       (p["player_id"],)).fetchone()
    fresh = (row and row["career_fetched"] and _age_days(row["career_fetched"]) < config.CAREER_TTL_DAYS
             and row["career_last_team"] == p["team_id"])
    if not fresh:
        try:
            rows, avg = espn.career(p["player_id"], season)
            conn.execute("DELETE FROM stints WHERE player_id=?", (p["player_id"],))
            for tid, s in rules.build_stints(rows).items():
                conn.execute("INSERT INTO stints VALUES(?,?,?,?,?,?,?,?)",
                             (p["player_id"], tid, s["abbr"], s["first_season"], s["last_season"], s["gp"],
                              int(s["left_midseason"]), s["left_year"]))
            if avg:
                conn.execute("INSERT OR REPLACE INTO season_stats VALUES(?,?,?,?,?,?,?)",
                             (p["player_id"], season, avg["gp"], avg["min"], avg["pts"], avg["reb"], avg["ast"]))
            conn.execute("UPDATE players SET career_fetched=?, career_last_team=? WHERE player_id=?",
                         (now_iso(), p["team_id"], p["player_id"]))
            conn.commit()
        except SourceError as e:
            warn.add("career", f"Career history unavailable for {p['name']}; used cached data if any ({e})")
    stints = {r["team_id"]: dict(r) for r in conn.execute("SELECT * FROM stints WHERE player_id=?", (p["player_id"],))}
    s = conn.execute("SELECT gp,min,pts,reb,ast FROM season_stats WHERE player_id=? AND season=?",
                     (p["player_id"], season)).fetchone()
    return stints, (dict(s) if s else None)


def ensure_place(conn, city, state, country, warn):
    try:
        return geocode.get_place(conn, city, state, country)
    except SourceError as e:
        warn.add("geocode", f"Coordinates unavailable for {city}, {state or country} ({e})")
        return None


def ensure_profile(conn, p, need_tx, warn):
    if not config.BBREF_ENABLED:
        return None
    try:
        return bbref.profile(conn, p["player_id"], p["name"], p.get("birth_date"), need_tx=need_tx)
    except SourceError as e:
        warn.add("bbref", f"Basketball-Reference unavailable for {p['name']} ({e})")
        return None


def where_from(conn, p, prof, hov, warn):
    """Places he is from, best first: manual override, then high school(s), then birthplace."""
    places = []
    if hov:
        places.append({"kind": "override", "label": hov["hometown"], "lat": hov.get("lat"), "lon": hov.get("lon"),
                       "note": hov.get("note")})
    else:
        for hs in (prof or {}).get("high_schools", []):
            g = ensure_place(conn, hs["city"], hs["region"], "", warn)
            places.append({"kind": "high_school", "school": hs["school"], "label": f"{hs['city']}, {hs['region']}",
                           "lat": g and g["lat"], "lon": g and g["lon"], "source_url": g and g["source_url"]})
    g = ensure_place(conn, p["birth_city"], p["birth_state"], p["birth_country"], warn)
    if g:
        places.append({"kind": "birthplace", "label": g["label"], "lat": g["lat"], "lon": g["lon"],
                       "source_url": g["source_url"]})
    return places


def ensure_games(conn, player_id, end_year, warn):
    """Compact game log for one season (cached; the current season refreshes every few hours)."""
    row = conn.execute("SELECT fetched, json FROM gamelog WHERE player_id=? AND end_year=?",
                       (player_id, end_year)).fetchone()
    cur = end_year == config.current_end_year()
    ttl = config.GAMELOG_TTL_HOURS / 24 if cur else 365
    if row and _age_days(row["fetched"]) < ttl:
        cached = json.loads(row["json"])
        if not cached or ("venue" in cached[0] and "tm" in cached[0]):   # older cached logs lack venue, team or Eastern dates: fetch again once
            return cached
    try:
        games = espn.gamelog(player_id, end_year)
    except SourceError as e:
        warn.add("gamelog", f"Game log unavailable ({e})")
        return json.loads(row["json"]) if row else []
    conn.execute("INSERT OR REPLACE INTO gamelog VALUES(?,?,?,?)", (player_id, end_year, now_iso(), json.dumps(games)))
    conn.commit()
    return games


def load_rivalries() -> list[dict]:
    """Curated, sourced player-vs-player history. Entries without a reason and a link are dropped."""
    path = config.ROOT / "config" / "rivalries.yaml"
    if not path.exists():
        return []
    out = []
    for r in (yaml.safe_load(path.read_text()) or {}).get("rivalries") or []:
        pl = r.get("players") or []
        if len(pl) == 2 and r.get("reason") and r.get("sources"):
            out.append(r)
    return out


def games_with_ids(conn, player_id, first_end_year, last_end_year, warn):
    """Season logs that include game ids (older cached logs without them are re-fetched once)."""
    out = []
    for y in range(first_end_year, last_end_year + 1):
        out += ensure_games(conn, player_id, y, warn)
    return out


def history_tags(conn, pa, pb, rv, slate_date, warn):
    """History tags for the two players of one rivalry. Returns (tag_for_a, tag_for_b)."""
    last = config.current_end_year(slate_date)
    first = max(2018, last - 9)
    la = games_with_ids(conn, pa["player_id"], first, last, warn)
    lb = games_with_ids(conn, pb["player_id"], first, last, warn)
    la = [g for g in la if g["date"] < slate_date.isoformat()]
    lb = [g for g in lb if g["date"] < slate_date.isoformat()]
    h = rules.head_to_head(la, lb)
    scope = f"{first - 1}-{str(first)[2:]} to now, regular season and playoffs"

    def tag(me, other, mine, theirs, rec):
        return {"category": "History", "kind": "rivalry", "label": rv.get("kind", "History"), "confidence": "high",
                "headline": f"{rv.get('kind', 'History')} history with {other['name']}.",
                "reason": rv["reason"], "detail": rv["reason"], "with": other["name"], "with_id": other["player_id"],
                "with_team": other["_team"], "sources": rv["sources"], "_score": 8,
                "h2h": {"scope": scope, "games": h["games"], "me": mine, "them": theirs, "record": rec,
                        "recent": [{"date": x["date"], "me": x["a_pts" if me is pa else "b_pts"],
                                    "them": x["b_pts" if me is pa else "a_pts"], "playoff": x["playoff"]}
                                   for x in h["recent"]]}}

    wl = h["a_record"].split("-")
    rec_b = f"{wl[1]}-{wl[0]}"
    return tag(pa, pb, h["a"], h["b"], h["a_record"]), tag(pb, pa, h["b"], h["a"], rec_b)


def player_logs(conn, player_id, slate_date, warn):
    """Every known game of his career (cached season logs, from his first season to now)."""
    last = config.current_end_year(slate_date)
    row = conn.execute("SELECT MIN(first_season) AS f FROM stints WHERE player_id=?", (player_id,)).fetchone()
    first = int(row["f"][:4]) + 1 if row and row["f"] else last - 9
    return games_with_ids(conn, player_id, max(first, last - 25), last, warn)


def career_for(conn, e, m, slate_date, warn):
    """Career special-game lines for one flagged player (only lines backed by real past games)."""
    cats = {t["category"] for t in m["tags"]}
    need_logs = bool(cats & {"Birthday", "Hometown"} or any(t.get("_exit") for t in m["tags"]))
    logs = player_logs(conn, e["player_id"], slate_date, warn) if need_logs else []
    return career.lines(logs, slate_date, m["birth"], m["tags"], e["opponent"], e["opponent_name"])


def prior_projections(slate_date) -> dict:
    """Projections already published for this day, by player id, so they can be kept once the game starts."""
    f = config.OUT / f"{slate_date.isoformat()}.json"
    try:
        return {x["player_id"]: x["projection"] for x in json.loads(f.read_text()).get("entries", []) if x.get("projection")}
    except (OSError, ValueError, KeyError):
        return {}


def projection_for(conn, e, table, slate_date, warn, prior):
    """Pre-game projection for one flagged player; after tip-off the one published before the game is kept."""
    if projection.started(e["tip_utc"]):
        return projection.freeze(None, prior.get(e["player_id"]), e["tip_utc"])
    end = config.current_end_year(slate_date)
    logs = ensure_games(conn, e["player_id"], end, warn) + ensure_games(conn, e["player_id"], end - 1, warn)
    fresh = nba_projection.project(logs, e["team"], nba_projection.opp_factors(table, e["opponent"]), slate_date,
                                   int(e["player_id"]) * 100003 + int(e["game_id"]))
    return projection.freeze(fresh, prior.get(e["player_id"]), e["tip_utc"])


def recent_games(conn, player_id, opp_abbr, slate_date, warn):
    """Last 5 games and last 5 against this opponent, looking back up to three seasons."""
    end = config.current_end_year(slate_date)
    games = []
    for y in (end, end - 1, end - 2):
        games += ensure_games(conn, player_id, y, warn)
        games = [g for g in games if g["date"] < (slate_date.isoformat())]
        vs = [g for g in games if g["opp"] == opp_abbr]
        if len(games) >= 5 and len(vs) >= 5:
            break
    games.sort(key=lambda g: g["date"], reverse=True)
    return rules.recent_summary(games, opp_abbr)


def load_roster(conn, tid, season, warn):
    try:
        roster = espn.roster(tid, season)
        for pl in roster:
            conn.execute(
                "INSERT INTO players(player_id,name,birth_date,birth_city,birth_state,birth_country,team_id,school,last_seen) "
                "VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(player_id) DO UPDATE SET name=excluded.name, "
                "birth_date=excluded.birth_date, birth_city=excluded.birth_city, birth_state=excluded.birth_state, "
                "birth_country=excluded.birth_country, team_id=excluded.team_id, school=excluded.school, "
                "last_seen=excluded.last_seen",
                (pl["player_id"], pl["name"], pl["birth_date"] and pl["birth_date"].isoformat(),
                 pl["birth_city"], pl["birth_state"], pl["birth_country"], tid, pl["school"], now_iso()))
        conn.commit()
        return roster
    except SourceError as e:
        warn.add("roster", f"Roster for {abbr(tid)} unavailable; using last cached roster ({e})")
        return [{"player_id": r["player_id"], "name": r["name"], "school": r["school"] or "",
                 "birth_city": r["birth_city"] or "", "birth_state": r["birth_state"] or "",
                 "birth_country": r["birth_country"] or "", "position": "", "jersey": "",
                 "birth_date": r["birth_date"] and date.fromisoformat(r["birth_date"])}
                for r in conn.execute("SELECT * FROM players WHERE team_id=?", (tid,))]


# ------------------------------------------------------------------- one player
def player_tags(conn, pl, tid, opp, is_home, game, slate_date, season, ov, warn):
    """Returns (tags, avg_stats, profile) for one rostered player; tags may be empty."""
    p = {**pl, "team_id": tid}
    tags = []
    t = rules.birthday_tag(pl["birth_date"], slate_date)
    if t:
        tags.append(t)
    stints, avg = ensure_career(conn, p, season, warn)
    st = dict(stints[opp]) if opp in stints else None
    manual = next((m.get("note") or "Manual revenge flag" for m in ov["revenge"]
                   if (m.get("player_id") == pl["player_id"]
                       or rules.norm_name(m.get("player", "")) == rules.norm_name(pl["name"]))
                   and team_id(m.get("team")) == opp), None)
    prof = ensure_profile(conn, p, need_tx=bool(st or manual), warn=warn)

    # hometown: prefer where he grew up
    hov = ov["hometown"].get(pl["player_id"]) or ov["hometown"].get(rules.norm_name(pl["name"]))
    places = where_from(conn, p, prof, hov, warn)
    venue = game["_venue"]
    ht = rules.hometown_tags(places, venue, tuple(TEAMS[opp][2:]), is_home, game["arena_city"], config.HOMETOWN_RADIUS_MI)
    for tag in ht:
        src = []
        used = next((x for x in places if x["kind"] == tag["kind"]), None)
        if tag["kind"] == "high_school" and prof:
            src.append({"label": "Basketball-Reference", "url": f"{bbref.BASE}/players/{prof['slug'][0]}/{prof['slug']}.html"})
        if used and used.get("source_url"):
            src.append({"label": "Place on Wikidata", "url": used["source_url"]})
        tag["sources"] = src
        if used and used.get("lat") is not None:
            tag["_place"] = (used["lat"], used["lon"])
    tags += ht

    # revenge / old team
    if st or manual:
        ext, src = None, []
        exits = rules.build_exits(prof["transactions"]) if prof else {}
        if opp in exits:
            ext = exits[opp]
            src.append({"label": "Basketball-Reference transactions",
                        "url": f"{bbref.BASE}/players/{prof['slug'][0]}/{prof['slug']}.html#all_transactions"})
        else:
            mv = transactions.confirmed_exit(conn, pl["name"], opp)
            if mv:
                ext = {"kind": "trade" if mv["type"] == "trade" else "waived", "date": mv["date"],
                       "to": mv["to_team_id"], "text": ""}
                src.append({"label": "ESPN transactions", "url": "https://www.espn.com/nba/transactions"})
        to_nick = nick(ext["to"]) if ext and ext.get("to") in TEAMS else None
        rv = rules.revenge_tag(st, ext, nick(opp), to_nick, manual, config.MIN_GP_FOR_REVENGE, slate_date.year)
        if rv:
            rv["_exit"] = ext["date"] if ext else None
            rv["sources"] = src or [{"label": "ESPN career history", "url": f"https://www.espn.com/nba/player/stats/_/id/{pl['player_id']}"}]
            tags.append(rv)
    return tags, avg


# ---------------------------------------------------------------------- main
def run(target: date | None = None, include_preseason=False, notify=False) -> dict:
    conn, warn, started = db.connect(), Warnings(), now_iso()
    geocode.reset()
    bbref.reset()
    ov = load_overrides()
    if config.TRANSACTIONS_CSV.exists():
        transactions.import_csv(conn, config.TRANSACTIONS_CSV)
    pre = []
    slate_date, games = espn.pick_slate(target, include_preseason, pre)
    for m in pre:
        warn.add("slate", m)
    season = config.current_season(slate_date)
    log.info("Slate %s: %d games", slate_date, len(games))

    try:
        n = transactions.save_trades(conn, espn.fetch_moves(), "espn")
        log.info("Trades and waivers: %d new", n)
    except SourceError as e:
        warn.add("trades", f"Trade feed unavailable; using career history only ({e})")

    rivalries = load_rivalries()
    entries, meta = [], {}
    for g in games:
        conn.execute("INSERT OR REPLACE INTO games VALUES(?,?,?,?,?,?)",
                     (g["game_id"], g["date"], g["tip_utc"], g["home_id"], g["away_id"], g["arena"]))
        venue = ensure_place(conn, g["arena_city"], g["arena_state"], "", warn)
        g["_venue"] = (venue["lat"], venue["lon"]) if venue else tuple(TEAMS[g["home_id"]][2:])
        rosters = {tid: load_roster(conn, tid, season, warn) for tid in (g["home_id"], g["away_id"])}
        names = {tid: {rules.norm_name(p["name"]): p for p in r} for tid, r in rosters.items()}
        hist = {}   # player_id -> [history tags]
        for rv in rivalries:
            a, b = (rules.norm_name(n) for n in rv["players"])
            for ta, tb in ((g["home_id"], g["away_id"]), (g["away_id"], g["home_id"])):
                if a in names[ta] and b in names[tb]:
                    pa, pb = dict(names[ta][a], _team=abbr(ta)), dict(names[tb][b], _team=abbr(tb))
                    t1, t2 = history_tags(conn, pa, pb, rv, slate_date, warn)
                    hist.setdefault(pa["player_id"], []).append(t1)
                    hist.setdefault(pb["player_id"], []).append(t2)
        for tid, opp, is_home in ((g["home_id"], g["away_id"], True), (g["away_id"], g["home_id"], False)):
            roster = rosters[tid]
            for pl in roster:
                if rules.norm_name(pl["name"]) in ov["ignore"]:
                    continue
                tags, avg = player_tags(conn, pl, tid, opp, is_home, g, slate_date, season, ov, warn)
                tags += hist.get(pl["player_id"], [])
                if career.holiday_name(slate_date) and avg and (avg.get("min") or 0) >= 12:
                    ht = career.holiday_tag(player_logs(conn, pl["player_id"], slate_date, warn), slate_date, abbr(opp), nick(opp))
                    if ht:
                        tags.append(ht)
                meta[pl["player_id"]] = {"birth": pl["birth_date"], "tags": tags}
                if not tags:
                    continue
                for t in tags:
                    conn.execute("INSERT OR REPLACE INTO flags VALUES(?,?,?,?,?,?)",
                                 (slate_date.isoformat(), g["game_id"], pl["player_id"], t["category"],
                                  t["detail"], t["confidence"]))
                    t.setdefault("sources", [])
                entries.append({
                    "player_id": pl["player_id"], "name": pl["name"], "team": abbr(tid), "team_name": nick(tid),
                    "opponent": abbr(opp), "opponent_name": nick(opp),
                    "position": pl.get("position", ""), "jersey": pl.get("jersey", ""),
                    "home_away": "home" if is_home else "away", "game_id": g["game_id"], "game_kind": g["kind"],
                    "tip": g["tip_local"], "tip_utc": g["tip_utc"], "arena": g["arena"],
                    "location": ", ".join(x for x in (g["arena_city"], g["arena_state"]) if x),
                    "categories": sorted({t["category"] for t in tags}),
                    "summary": " ".join(t["headline"] for t in tags[:2]),
                    "tags": [{k: v for k, v in t.items() if not k.startswith("_")} for t in tags],
                    "score": round(len(tags) * 10 + max((t.get("_score", 0) for t in tags), default=0), 2),
                    "stats": avg, "espn_url": f"https://www.espn.com/nba/player/_/id/{pl['player_id']}",
                    "recent": None, "headshot": None, "team_logo": None, "opponent_logo": None})
    conn.commit()

    # how soft or tough each opponent's defense is for the player's position (from this season's box scores)
    try:
        table = matchups.build_table(matchups.load_boxes(conn, slate_date, warn))
    except Exception as e:   # never lose the whole slate over this extra
        warn.add("matchups", f"Matchup grades unavailable ({e})")
        table = {}
    for e in entries:
        e["matchup"] = matchups.matchup(table, e["opponent"], e["position"])

    # extras for flagged players only: recent games and images
    logos = {a: media.team_logo(a) for a in {x for g in games for x in (abbr(g["home_id"]), abbr(g["away_id"]))}}
    prior = prior_projections(slate_date)
    for e in entries:
        e["career"] = career_for(conn, e, meta[e["player_id"]], slate_date, warn)
        e["projection"] = projection_for(conn, e, table, slate_date, warn, prior)
        e["recent"] = recent_games(conn, e["player_id"], e["opponent"], slate_date, warn)
        if e["recent"]["vs"]["n"] == 0 and any(t.get("kind") in ("trade", "waived") for t in e["tags"]):
            e["recent"]["vs"]["note"] = f"First meeting with the {e['opponent_name']} since he left."
        e["headshot"] = media.headshot(e["player_id"])
        e["team_logo"], e["opponent_logo"] = logos.get(e["team"]), logos.get(e["opponent"])
    for g in games:
        g.pop("_venue", None)

    entries.sort(key=lambda e: (-e["score"], e["tip_utc"], e["name"]))
    warnings = warn.finish()
    slate = {"date": slate_date.isoformat(), "generated_at": now_iso() + "Z", "season": season,
             "games": len(games), "entries": entries, "warnings": warnings,
             "matchups": [{"away": abbr(g["away_id"]), "home": abbr(g["home_id"]), "tip": g["tip_local"],
                           "away_logo": logos.get(abbr(g["away_id"])), "home_logo": logos.get(abbr(g["home_id"]))}
                          for g in games]}
    output.write_slate(slate)
    conn.execute("INSERT INTO runs(started,finished,slate_date,status,warnings) VALUES(?,?,?,?,?)",
                 (started, now_iso(), slate["date"], "ok" if not warnings else "degraded", json.dumps(warnings)))
    conn.commit()
    if notify:
        from . import notify as n
        n.send(slate)
    return slate
