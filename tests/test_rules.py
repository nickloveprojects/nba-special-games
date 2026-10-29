from datetime import date

from app import rules


def test_birthday_and_leap():
    assert rules.birthday_tag(date(1998, 10, 28), date(2026, 10, 28))["detail"] == "Turns 28 today"
    assert rules.birthday_tag(date(1998, 10, 29), date(2026, 10, 28)) is None
    assert "observed Feb 28" in rules.birthday_tag(date(2000, 2, 29), date(2027, 2, 28))["detail"]
    assert rules.birthday_tag(date(2000, 2, 29), date(2028, 2, 28)) is None


CHI = (41.881, -87.674)
PDX = (45.532, -122.667)
DC = (38.898, -77.021)


def _p(kind, label, lat, lon, **kw):
    return {"kind": kind, "label": label, "lat": lat, "lon": lon, **kw}


def test_hometown_prefers_where_he_grew_up():
    # Born in Portland, raised in Hyattsville MD (the Jerami Grant case)
    places = [_p("high_school", "Hyattsville, Maryland", 38.956, -76.945, school="DeMatha Catholic"),
              _p("birthplace", "Portland, OR", 45.52, -122.68)]
    assert rules.hometown_tags(places, PDX, DC, False, "Portland", 25) == []             # born here, raised elsewhere
    t = rules.hometown_tags(places, DC, PDX, False, "Washington", 25)[0]                  # playing near where he grew up
    assert t["kind"] == "high_school" and t["confidence"] == "high" and "DeMatha" in t["detail"]


def test_hometown_birthplace_only_is_low_confidence():
    places = [_p("birthplace", "Chicago, IL", 41.878, -87.63)]
    t = rules.hometown_tags(places, CHI, PDX, False, "Chicago", 25)[0]
    assert t["confidence"] == "low" and "couldn't confirm" in t["headline"]
    assert rules.hometown_tags([], CHI, PDX, False, "Chicago", 25) == []
    # high school listed but its location could not be found: still low, says so
    places = [_p("high_school", "Nowhere, X", None, None, school="S"), places[0]]
    assert "location not found" in rules.hometown_tags(places, CHI, PDX, False, "Chicago", 25)[0]["detail"]


def test_hometown_override_and_visiting_team():
    ov = [_p("override", "Akron, OH", 41.08, -81.52, note="raised there")]
    assert rules.hometown_tags(ov, (41.5, -81.69), PDX, True, "Cleveland", 40)[0]["confidence"] == "high"
    hs = [_p("high_school", "Chicago, Illinois", 41.878, -87.63, school="Simeon")]
    t = rules.hometown_tags(hs, (43.6, -79.4), CHI, True, "Toronto", 25)[0]               # home team hosts the Bulls
    assert t["where"] == "opponent"


def test_stints_midseason_and_return():
    rows = [
        {"SEASON_ID": "2022-23", "TEAM_ID": 1610612747, "TEAM_ABBREVIATION": "LAL", "GP": 60},
        {"SEASON_ID": "2023-24", "TEAM_ID": 0, "TEAM_ABBREVIATION": "TOT", "GP": 70},
        {"SEASON_ID": "2023-24", "TEAM_ID": 1610612747, "TEAM_ABBREVIATION": "LAL", "GP": 40},
        {"SEASON_ID": "2023-24", "TEAM_ID": 1610612738, "TEAM_ABBREVIATION": "BOS", "GP": 30},
        {"SEASON_ID": "2024-25", "TEAM_ID": 1610612738, "TEAM_ABBREVIATION": "BOS", "GP": 70},
    ]
    s = rules.build_stints(rows)
    assert s[1610612747]["left_midseason"] and s[1610612747]["gp"] == 100 and s[1610612747]["left_year"] == 2024
    assert not s[1610612738]["left_midseason"]


GRANT_LOG = [
    {"date": "2014-06-26", "kind": "draft", "teams": ["PHI"], "text": "Drafted by the Philadelphia 76ers"},
    {"date": "2016-11-01", "kind": "trade", "teams": ["PHI", "OKC"], "text": "Traded by the Philadelphia 76ers to the Oklahoma City Thunder for Ersan Ilyasova."},
    {"date": "2018-07-07", "kind": "fa_sign", "teams": ["OKC"], "text": "Signed as a free agent with the Oklahoma City Thunder."},
    {"date": "2019-07-08", "kind": "trade", "teams": ["OKC", "DEN"], "text": "Traded by the Oklahoma City Thunder to the Denver Nuggets for a 2020 1st round draft pick."},
    {"date": "2021-09-06", "kind": "waive", "teams": ["DET"], "text": "Waived by the Detroit Pistons. $4M buyout"},
    {"date": "2021-09-20", "kind": "fa_sign", "teams": ["LAL"], "text": "Signed as a free agent with the Los Angeles Lakers."},
    {"date": "2023-07-09", "kind": "sign", "teams": ["POR"], "text": "Signed a multi-year contract with the Portland Trail Blazers."},
    {"date": "2026-06-29", "kind": "trade", "teams": ["POR", "MEM"],
     "text": "Traded by the Portland Trail Blazers with Kris Murray to the Memphis Grizzlies for Ja Morant and cash. Memphis received a trade exception. Portland received a trade exception."},
]


def test_build_exits_classifies_trade_waiver_and_free_agency():
    ex = rules.build_exits(GRANT_LOG)
    POR, OKC, DET, LAL, MEM = 1610612757, 1610612760, 1610612765, 1610612747, 1610612763
    assert ex[POR]["kind"] == "trade" and ex[POR]["to"] == MEM and ex[POR]["date"] == "2026-06-29"
    assert ex[DET]["kind"] == "waived"
    assert ex[OKC]["kind"] == "trade"
    # Lakers: signed as free agent, then POR "sign" while current team was LAL -> left in free agency
    assert ex[LAL]["kind"] == "free_agency" and ex[LAL]["to"] == POR


def test_revenge_wording_and_confidence():
    ext = {"kind": "trade", "date": "2026-06-29", "to": 1610612757, "text": GRANT_LOG[-1]["text"]}
    st = {"first_season": "2022-23", "last_season": "2025-26", "gp": 221, "left_midseason": False, "left_year": 2026}
    t = rules.revenge_tag(st, ext, "Trail Blazers", "Grizzlies", None, 15, 2026)
    assert t["confidence"] == "high" and t["kind"] == "trade"
    assert t["headline"] == "Faces the Trail Blazers, who traded him on Jun 29, 2026."
    assert t["how_left"] == "Traded to the Grizzlies for Ja Morant and cash (Jun 29, 2026)."
    fa = rules.revenge_tag(st, {"kind": "free_agency", "date": "2024-07-01", "to": 1, "text": ""}, "Lakers", "Heat", None, 15, 2026)
    assert fa["confidence"] == "medium" and "free agency" in fa["headline"]
    unk = rules.revenge_tag(st, None, "Lakers", None, None, 15, 2026)
    assert unk["confidence"] == "low" and unk["how_left"] == "How he left isn't confirmed yet."
    assert rules.revenge_tag({**st, "left_midseason": True}, None, "Lakers", None, None, 15, 2026)["confidence"] == "medium"
    assert rules.revenge_tag({**st, "gp": 3}, None, "Lakers", None, None, 15, 2026) is None   # cup of coffee
    assert rules.revenge_tag({**st, "gp": 3}, ext, "Lakers", None, None, 15, 2026) is None    # < 5 games even with a trade
    assert rules.revenge_tag(None, ext, "Lakers", None, None, 15, 2026) is None
    assert rules.revenge_tag(None, None, "Lakers", None, "Requested trade", 15, 2026)["confidence"] == "high"


def test_recent_summary():
    gs = [{"date": f"2026-10-{d:02d}", "opp": "POR" if d % 2 else "LAL", "pts": d, "reb": 1, "ast": 2, "min": 30,
           "home": True, "result": "W", "score": "1-0", "playoff": False} for d in range(28, 10, -1)]
    r = rules.recent_summary(gs, "POR")
    assert r["form"]["n"] == 5 and r["form"]["pts"] == 26.0
    assert r["vs"]["n"] == 5 and all(g["opp"] == "POR" for g in r["vs"]["games"])
    assert rules.recent_summary([], "POR")["vs"]["n"] == 0


def test_names():
    assert rules.norm_name("Jaren Jackson Jr.") == rules.norm_name("jaren jackson")
    assert rules.name_similarity("Luka Dončić", "Luka Doncic") > 0.95
