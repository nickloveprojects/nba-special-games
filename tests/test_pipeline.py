import json
from datetime import date

from app import config, pipeline
from app.net import SourceError
from app.sources import bbref, espn, geocode, media

LAL, BOS, CHI, POR, MEM = 1610612747, 1610612738, 1610612741, 1610612757, 1610612763


def _game(gid, d, home, away, hn, an, arena="United Center", city="Chicago", state="IL"):
    return {"game_id": gid, "kind": "Regular season", "date": d, "tip_utc": d + "T23:00:00+00:00",
            "tip_local": "8:00 PM ET", "home_id": home, "away_id": away, "home_name": hn, "away_name": an,
            "arena": arena, "arena_city": city, "arena_state": state}


def _pl(pid, name, birth, city="", state="", pos="G", jersey="1"):
    return {"player_id": pid, "name": name, "birth_date": birth, "birth_city": city, "birth_state": state,
            "birth_country": "USA", "school": "", "position": pos, "jersey": jersey}


def _stub_media(monkeypatch):
    monkeypatch.setattr(media, "team_logo", lambda a: f"img/teams/{a}.png")
    monkeypatch.setattr(media, "headshot", lambda pid: f"img/players/{pid}.png")
    monkeypatch.setattr(espn, "gamelog", lambda pid, y: [
        {"date": "2026-04-01", "opp": "POR", "home": True, "result": "W", "score": "1-0", "min": 30, "pts": 20, "reb": 5,
         "ast": 4, "playoff": False}] if y == 2026 else [])


def test_end_to_end(monkeypatch):
    # Memphis (away) at Portland: Grant was raised in Maryland, born in Portland -> NOT a hometown game;
    # Morant (Portland, away team's old club is Memphis) -> traded away, confirmed by the log.
    game = _game("401", "2026-10-29", POR, MEM, "Portland Trail Blazers", "Memphis Grizzlies", "Moda Center", "Portland", "OR")
    monkeypatch.setattr(espn, "pick_slate", lambda *a, **k: (date(2026, 10, 29), [game]))
    monkeypatch.setattr(espn, "fetch_moves", lambda: [])
    rosters = {MEM: [_pl(1, "Jerami Grant", date(1994, 3, 12), "Portland", "OR", "F", "31"),
                     _pl(2, "Plain Guy", date(1995, 1, 1), "Nowhere", "TX")],
               POR: [_pl(3, "Ja Morant", date(1999, 8, 10), "Dalzell", "SC", "G", "12"),
                     _pl(4, "Birthday Boy", date(2001, 10, 29), "Seattle", "WA")]}
    monkeypatch.setattr(espn, "roster", lambda tid, season="": rosters[tid])

    def career(pid, season):
        if pid == 1:
            return [{"SEASON_ID": "2025-26", "TEAM_ID": POR, "TEAM_ABBREVIATION": "POR", "GP": 70}], {"gp": 1, "min": 30.0, "pts": 20.0, "reb": 5.0, "ast": 4.0}
        if pid == 3:
            return [{"SEASON_ID": "2025-26", "TEAM_ID": MEM, "TEAM_ABBREVIATION": "MEM", "GP": 60}], None
        return [], None

    monkeypatch.setattr(espn, "career", career)
    places = {"Portland": (45.52, -122.68), "Hyattsville": (38.956, -76.945), "Dalzell": (33.9, -80.4), "Seattle": (47.6, -122.3)}
    monkeypatch.setattr(geocode, "lookup", lambda city, st, co: (
        {"lat": places[city][0], "lon": places[city][1], "source_url": "https://www.wikidata.org/wiki/Q1"} if city in places else None))

    def prof(conn, pid, name, birth, need_tx=True):
        if pid == 1:
            return {"slug": "grantje01", "high_schools": [{"school": "DeMatha Catholic", "city": "Hyattsville", "region": "Maryland"}],
                    "transactions": [{"date": "2023-07-09", "kind": "sign", "teams": ["POR"], "text": "Signed with POR"},
                                     {"date": "2026-06-29", "kind": "trade", "teams": ["POR", "MEM"],
                                      "text": "Traded by the Portland Trail Blazers with Kris Murray to the Memphis Grizzlies for Ja Morant and cash."}]}
        if pid == 3:
            return {"slug": "moranja01", "high_schools": [],
                    "transactions": [{"date": "2019-06-20", "kind": "draft", "teams": ["MEM"], "text": "Drafted"},
                                     {"date": "2026-06-29", "kind": "trade", "teams": ["MEM", "POR"],
                                      "text": "Traded by the Memphis Grizzlies to the Portland Trail Blazers for Jerami Grant and Kris Murray."}]}
        return None

    monkeypatch.setattr(bbref, "profile", prof)
    _stub_media(monkeypatch)
    slate = pipeline.run(date(2026, 10, 29))
    by = {e["name"]: e for e in slate["entries"]}
    assert set(by) == {"Jerami Grant", "Ja Morant", "Birthday Boy"}            # Plain Guy not flagged
    g = by["Jerami Grant"]
    assert g["categories"] == ["Revenge"]                                       # born in Portland, raised in Maryland
    assert g["team_name"] == "Grizzlies" and g["position"] == "F" and g["jersey"] == "31"
    rv = g["tags"][0]
    assert rv["kind"] == "trade" and rv["confidence"] == "high"
    assert "Traded to the Grizzlies for Ja Morant and cash" in rv["how_left"]
    assert g["summary"].startswith("Faces the Trail Blazers, who traded him on Jun 29, 2026.")
    assert g["recent"]["vs"]["n"] == 1 and g["recent"]["vs"]["opp"] == "POR"
    assert g["headshot"] == "img/players/1.png" and g["team_logo"] == "img/teams/MEM.png"
    assert by["Ja Morant"]["tags"][0]["how_left"].startswith("Traded to the Trail Blazers")
    assert by["Birthday Boy"]["categories"] == ["Birthday"]
    assert json.loads((config.OUT / "index.json").read_text())["latest"] == "2026-10-29"


def test_source_failure_degrades(monkeypatch):
    game = _game("x", "2026-10-30", CHI, BOS, "Chicago Bulls", "Boston Celtics", arena="")
    monkeypatch.setattr(espn, "pick_slate", lambda *a, **k: (date(2026, 10, 30), [game]))

    def boom(*a, **k):
        raise SourceError("down")

    monkeypatch.setattr(espn, "fetch_moves", boom)
    monkeypatch.setattr(espn, "roster", boom)
    monkeypatch.setattr(geocode, "lookup", boom)
    monkeypatch.setattr(bbref, "profile", boom)
    _stub_media(monkeypatch)
    slate = pipeline.run(date(2026, 10, 30))
    assert slate["warnings"] and slate["entries"] == []


def test_history_rivalry(monkeypatch):
    HOU, MIL = 1610612745, 1610612749
    game = _game("500", "2026-10-28", MIL, HOU, "Milwaukee Bucks", "Houston Rockets", "Fiserv Forum", "Milwaukee", "WI")
    monkeypatch.setattr(espn, "pick_slate", lambda *a, **k: (date(2026, 10, 28), [game]))
    monkeypatch.setattr(espn, "fetch_moves", lambda: [])
    rosters = {HOU: [_pl(10, "Amen Thompson", date(2002, 1, 30), "Oakland", "CA", "G", "1")],
               MIL: [_pl(11, "Tyler Herro", date(2000, 1, 20), "Milwaukee", "WI", "G", "14")]}
    monkeypatch.setattr(espn, "roster", lambda tid, season="": rosters[tid])
    monkeypatch.setattr(espn, "career", lambda pid, season: ([], None))
    monkeypatch.setattr(geocode, "lookup", lambda *a: None)
    monkeypatch.setattr(bbref, "profile", lambda *a, **k: None)
    monkeypatch.setattr(media, "team_logo", lambda a: f"img/teams/{a}.png")
    monkeypatch.setattr(media, "headshot", lambda pid: f"img/players/{pid}.png")

    def log(pid, y):
        row = lambda gid, d, opp, res, pts: {"gid": gid, "date": d, "opp": opp, "home": True, "result": res,  # noqa: E731
                                              "score": "1-0", "min": 30, "pts": pts, "reb": 4, "ast": 5, "playoff": False}
        if y != 2026:
            return []
        if pid == 10:
            return [row("g1", "2025-01-01", "MIL", "W", 20), row("g2", "2025-02-01", "MIL", "L", 10), row("g9", "2025-03-01", "BOS", "W", 5)]
        return [row("g1", "2025-01-01", "HOU", "L", 30), row("g2", "2025-02-01", "HOU", "W", 20)]

    monkeypatch.setattr(espn, "gamelog", log)
    slate = pipeline.run(date(2026, 10, 28))
    by = {e["name"]: e for e in slate["entries"]}
    amen = next(t for t in by["Amen Thompson"]["tags"] if t["category"] == "History")
    assert by["Amen Thompson"]["team_name"] == "Rockets" and "History" in by["Tyler Herro"]["categories"]
    assert amen["with"] == "Tyler Herro" and amen["sources"] and "ejected" in amen["reason"]
    h = amen["h2h"]
    assert h["games"] == 2 and h["record"] == "1-1" and h["me"]["pts"] == 15.0 and h["them"]["pts"] == 25.0
    herro = next(t for t in by["Tyler Herro"]["tags"] if t["category"] == "History")
    assert herro["h2h"]["me"]["pts"] == 25.0


def test_head_to_head_no_shared_games():
    from app import rules
    h = rules.head_to_head([{"gid": "1", "date": "d", "result": "W", "pts": 1, "min": 1, "reb": 1, "ast": 1, "playoff": False}], [])
    assert h["games"] == 0 and h["a"] == {"n": 0}
