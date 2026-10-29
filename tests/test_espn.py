from app.sources import espn


def test_parse_trade():
    assert espn.parse_trade("Acquired G Rob Dillingham from Chicago Bulls for G Buddy Hield.") == (
        ["Rob Dillingham"], 1610612741)
    names, frm = espn.parse_trade("Acquired F Jo Smith, G Al Jones and a 2028 2nd round pick from LA Clippers.")
    assert names == ["Jo Smith", "Al Jones"] and frm == 1610612746
    assert espn.parse_trade("Signed F Enrique Freeman to a two-way contract.") is None
    assert espn.parse_trade("Acquired G Someone from Some G League Team.") is None


def test_parse_roster():
    data = {"athletes": [{"id": "4066328", "fullName": "Jarrett Allen", "dateOfBirth": "1998-04-21T07:00Z",
                          "birthPlace": {"city": "Round Rock", "state": "TX", "country": "USA"},
                          "college": {"name": "Texas"}, "position": {"abbreviation": "C"}},
                         {"id": "9", "fullName": "No Bio"}]}
    a, b = espn.parse_roster(data)
    assert a["birth_date"].isoformat() == "1998-04-21" and a["birth_city"] == "Round Rock" and a["school"] == "Texas"
    assert b["birth_date"] is None and b["birth_city"] == ""


def test_parse_career():
    data = {"teams": {"brooklyn-nets": {"id": "17", "abbreviation": "BKN"},
                      "cleveland-cavaliers": {"id": "5", "abbreviation": "CLE"},
                      "new-jersey-nets": {"id": "99", "abbreviation": "NJ"}},
            "categories": [{"name": "averages", "labels": ["GP", "MIN", "REB", "AST", "PTS"], "statistics": [
                {"teamId": "17", "season": {"displayName": "2017-18"}, "stats": ["72", "20.0", "5.4", "0.7", "8.2"]},
                {"teamId": "5", "season": {"displayName": "2026-27"}, "stats": ["3", "31.5", "9.0", "2.0", "14.3"]},
                {"stats": ["x"]}]}]}
    rows, avg = espn.parse_career(data, "2026-27")
    assert [r["TEAM_ABBREVIATION"] for r in rows] == ["BKN", "CLE"] and rows[0]["GP"] == 72
    assert avg == {"gp": 3, "min": 31.5, "pts": 14.3, "reb": 9.0, "ast": 2.0}


def test_parse_events_skips_unknown_teams():
    ev = lambda hid, aid, kind=2: {"id": "1", "date": "2026-10-29T00:00Z", "season": {"type": kind}, "competitions": [{  # noqa: E731
        "competitors": [{"homeAway": "home", "team": {"id": str(hid), "displayName": "H"}},
                        {"homeAway": "away", "team": {"id": str(aid), "displayName": "A"}}],
        "venue": {"fullName": "Arena", "address": {"city": "Chicago", "state": "IL"}}}]}
    g = espn.parse_events({"events": [ev(4, 18), ev(4, 999), ev(4, 18, kind=1)]})
    assert len(g) == 1 and g[0]["tip_local"] == "8:00 PM ET" and g[0]["date"] == "2026-10-28"


def test_parse_waive():
    assert espn.parse_waive("Waived G Dwight Murray Jr. and G Isaiah Wong.") == ["Dwight Murray Jr", "Isaiah Wong"]
    assert espn.parse_waive("Signed F Someone to a contract.") is None


def test_roster_has_jersey():
    a = espn.parse_roster({"athletes": [{"id": "1", "fullName": "A B", "jersey": "31", "position": {"abbreviation": "F"}}]})[0]
    assert a["jersey"] == "31" and a["position"] == "F"


def test_parse_gamelog():
    data = {"names": ["minutes", "totalRebounds", "assists", "points"],
            "events": {"1": {"gameDate": "2026-10-28T00:30:00.000+00:00", "atVs": "@", "gameResult": "W", "score": "120-110",
                             "homeTeamId": "9", "opponent": {"abbreviation": "GS"}},
                       "2": {"gameDate": "2026-04-01T00:00:00.000+00:00", "atVs": "vs", "gameResult": "L", "score": "99-100",
                             "opponent": {"abbreviation": "UTAH"}}},
            "seasonTypes": [{"displayName": "2026-27 Regular Season", "categories": [{"events": [
                                {"eventId": "1", "stats": ["31", "7", "4", "22"]}]}]},
                            {"displayName": "2025-26 Preseason", "categories": [{"events": [{"eventId": "2", "stats": ["1", "1", "1", "1"]}]}]},
                            {"displayName": "2025-26 Postseason", "categories": [{"events": [{"eventId": "2", "stats": ["30", "5", "6", "18"]}]}]}]}
    g = espn.parse_gamelog(data)
    assert [x["opp"] for x in g] == ["GSW", "UTA"] and g[0]["pts"] == 22 and not g[0]["home"]
    assert g[1]["playoff"] and g[1]["ast"] == 6


def test_gamelog_uses_eastern_date_and_venue():
    data = {"names": ["points"], "events": {"1": {"gameDate": "2026-10-28T00:30:00.000+00:00", "atVs": "@", "gameResult": "W",
            "score": "1-0", "homeTeamId": "9", "opponent": {"abbreviation": "GS"}}},
            "seasonTypes": [{"displayName": "2026-27 Regular Season", "categories": [{"events": [{"eventId": "1", "stats": ["5"]}]}]}]}
    g = espn.parse_gamelog(data)[0]
    assert g["date"] == "2026-10-27" and g["venue"] == "GSW"
