from datetime import date

from app import nfl, nfl_feed as feed

LOG = lambda **r: {"gid": "1", "date": "2025-12-25", "season": 2025, "post": False, "team_id": 1, "opp_id": 2,
                   "opp": "DAL", "home": True, "home_id": 1, "result": "W", "week": 16, "row": r}


def test_summary_by_position():
    qb = [LOG(passingYards=300, passingTouchdowns=3, interceptions=1), LOG(passingYards=200, passingTouchdowns=1, interceptions=0)]
    assert nfl.summary("QB", qb) == "avg 250 pass yds, 2 TD, 0.5 INT"
    wr = [LOG(receptions=6, receivingYards=80, receivingTouchdowns=1)]
    assert nfl.summary("WR", wr) == "avg 6 rec, 80 yds, 1 TD"
    rb = [LOG(rushingYards=100, rushingTouchdowns=1, receivingTouchdowns=1, receptions=3)]
    assert nfl.summary("RB", rb) == "avg 100 rush yds, 2 TD, 3 rec"


def test_gamelog_parses_kicker_made_attempts():
    data = {"names": ["fieldGoalsMade-fieldGoalAttempts", "totalKickingPoints"],
            "events": {"9": {"id": "9", "gameDate": "2026-09-15T00:15:00.000+00:00", "atVs": "vs", "homeTeamId": "12",
                             "team": {"id": "12"}, "opponent": {"id": "7", "abbreviation": "DEN"}, "gameResult": "W", "week": 1}},
            "seasonTypes": [{"displayName": "2026 Regular Season",
                             "categories": [{"events": [{"eventId": "9", "stats": ["2-3", "9"]}]}]}]}
    g = feed.parse_gamelog(data, 2026)[0]
    assert g["row"]["fieldGoalsMade-fieldGoalAttempts.made"] == 2 and g["row"]["fieldGoalsMade-fieldGoalAttempts.att"] == 3
    assert g["date"] == "2026-09-14"          # 8:15 pm Eastern the day before the UTC date
    assert g["home"] and g["opp"] == "DEN"


def test_matchup_ranks_defenses_by_position():
    def box(a, b, ya, yb):
        row = lambda y: {"passing.passingYards": str(y), "passing.passingTouchdowns": "1"}
        return {a: {"1": row(ya)}, b: {"2": row(yb)}}
    posmap = {1: "QB", 2: "QB"}
    games = [nfl.box_groups(box("AAA", "BBB", 300, 100), posmap), nfl.box_groups(box("CCC", "DDD", 250, 200), posmap)]
    table = nfl.build_table(games)
    assert table["BBB"]["QB"]["pass_yds"] == 300      # BBB's defense faced AAA's 300 yards
    m = nfl.matchup(table, "BBB", "QB")
    assert m["stats"]["pass_yds"]["rank"] == 1 and m["stats"]["pass_yds"]["color"] == "green"
    assert nfl.matchup(table, "AAA", "QB")["stats"]["pass_yds"]["color"] == "red"
    assert nfl.matchup(table, "BBB", "K") is None


TEAMS = {7: {"id": 7, "abbr": "DEN", "short": "Broncos", "name": "Denver Broncos"},
         12: {"id": 12, "abbr": "KC", "short": "Chiefs", "name": "Kansas City Chiefs"},
         22: {"id": 22, "abbr": "ARI", "short": "Cardinals", "name": "Arizona Cardinals"}}


def _logs(*stints):
    out = []
    for team, dates in stints:
        for d in dates:
            out.append(dict(LOG(), team_id=team, date=d, season=int(d[:4])))
    return out


def test_exit_found_from_the_old_team_trade():
    rows = [{"date": "2025-03-10", "team": "DEN", "name": "Denver Broncos",
             "text": "Traded WR Some Guy and a 2026 pick to Kansas City for a 2025 sixth-round pick. Signed K A B."}]
    logs = _logs((7, ["2024-09-08", "2024-12-29"]), (12, ["2025-09-07"]))
    ex = nfl.exit_for({"name": "Some Guy"}, TEAMS[7], logs, lambda y: rows if y == 2025 else [], TEAMS, "2026-10-29")
    assert ex["kind"] == "trade" and ex["date"] == "2025-03-10" and ex["text"].startswith("Traded WR Some Guy")


def test_later_signing_is_reported_as_a_fact_not_as_free_agency():
    rows = [{"date": "2025-03-14", "team": "KC", "name": "Kansas City Chiefs", "text": "Signed WR Some Guy to a two-year contract."},
            {"date": "2025-03-15", "team": "ARI", "name": "Arizona Cardinals", "text": "Signed WR Some Guy to the practice squad."}]
    logs = _logs((7, ["2024-12-29"]), (12, ["2025-09-07"]))
    ex = nfl.exit_for({"name": "Some Guy"}, TEAMS[7], logs, lambda y: rows, TEAMS, "2026-10-29")
    assert ex["kind"] == "signed_elsewhere" and ex["new"] == "Chiefs"
    tag = nfl.revenge_tag({"name": "Some Guy"}, TEAMS[7], _logs((7, [f"2023-0{m}-10" for m in range(1, 7)]), (12, ["2025-09-07"])),
                          lambda y: rows, TEAMS, "2026-10-29")
    assert tag["kind"] == "unknown" and tag["confidence"] == "low" and "next signing was with the Chiefs" in tag["how_left"]


def test_trade_found_from_the_new_clubs_side_only():
    rows = [{"date": "2025-03-10", "team": "KC", "name": "Kansas City Chiefs",
             "text": "Traded a 2026 second-round pick in exchange for TE Some Guy and a 2027 fifth-round pick."}]
    logs = _logs((7, ["2024-12-29"]), (12, ["2025-09-07"]))
    ex = nfl.exit_for({"name": "Some Guy"}, TEAMS[7], logs, lambda y: rows, TEAMS, "2026-10-29")
    assert ex["kind"] == "trade_new_side" and ex["date"] == "2025-03-10"
    tag = nfl.revenge_tag({"name": "Some Guy"}, TEAMS[7], _logs((7, [f"2023-0{m}-10" for m in range(1, 7)] + ["2024-12-29"]), (12, ["2025-09-07"])),
                          lambda y: rows, TEAMS, "2026-10-29")
    assert tag["kind"] == "trade" and tag["confidence"] == "high" and tag["how_left"].startswith("Traded to the Chiefs.")
    assert tag["headline"] == "Traded by the Broncos."


def test_other_release_wordings_count():
    for txt in ("Waived/injured WR Some Guy.", "Terminated the contract of WR Some Guy."):
        pass
    rows = [{"date": "2025-03-10", "team": "DEN", "name": "Denver Broncos", "text": "Waived/injured WR Some Guy."}]
    logs = _logs((7, ["2024-12-29"]), (12, ["2025-09-07"]))
    assert nfl.exit_for({"name": "Some Guy"}, TEAMS[7], logs, lambda y: rows, TEAMS, "2026-10-29")["kind"] == "waived"


def test_pro_bowl_games_do_not_end_the_search_window():
    rows = [{"date": "2025-03-10", "team": "DEN", "name": "Denver Broncos", "text": "Released WR Some Guy."}]
    logs = _logs((7, ["2024-12-29"]), (99, ["2025-02-02"]), (12, ["2025-09-07"]))     # 99 = an all-star team, not a club
    ex = nfl.exit_for({"name": "Some Guy"}, TEAMS[7], logs, lambda y: rows, TEAMS, "2026-10-29")
    assert ex and ex["kind"] == "waived"


def test_clip_keeps_only_the_players_own_part():
    sent = "Released S Rudy Ford, WR Laquon Treadwell, LBs Tyrell Adams and Chapelle Russell, DL Auzoyah Alufohai."
    assert nfl.clip(sent, "Laquon Treadwell") == "Released WR Laquon Treadwell."
    one = "Released WR Some Guy from the practice squad."
    assert nfl.clip(one, "Some Guy") == one


def test_exit_none_when_the_log_has_nothing_about_the_player():
    logs = _logs((7, ["2024-12-29"]), (12, ["2025-09-07"]))
    assert nfl.exit_for({"name": "Nobody Here"}, TEAMS[7], logs, lambda y: [], TEAMS, "2026-10-29") is None


def test_sentence_split_keeps_jr_together():
    s = feed._sentences("Traded WR Marvin Harrison Jr. and a 2027 pick to Houston for picks. Signed K A B.")
    assert s[0].startswith("Traded WR Marvin Harrison Jr. and a 2027 pick") and len(s) == 2


def test_revenge_needs_real_games_with_the_team():
    opp = {"id": 7, "abbr": "DEN", "short": "Broncos", "name": "Denver Broncos"}
    few = [dict(LOG(), team_id=7, season=2024)] * 3
    assert nfl.revenge_tag({"name": "X"}, opp, few, lambda y: [], {}, "2026-10-29") is None
    many = [dict(LOG(), team_id=7, season=2023)] * 4 + [dict(LOG(), team_id=7, season=2025)] * 4
    t = nfl.revenge_tag({"name": "X"}, opp, many, lambda y: [], {7: opp}, "2026-10-29")
    assert t["kind"] == "unknown" and t["confidence"] == "low" and "from 2023 to 2025 (8 games)" in t["how_left"]


def test_holiday_tag_uses_only_past_holiday_games():
    d = date(2026, 11, 26)    # Thanksgiving
    past = dict(LOG(receptions=5, receivingYards=60, receivingTouchdowns=1), date="2024-11-28", opp="DAL")
    t = nfl.holiday_tag({"pos": "WR"}, [past], d, "DAL", "Cowboys")
    assert t["label"] == "Thanksgiving" and "1 time" in t["lines"][0]["text"] and len(t["lines"]) == 3
    assert nfl.holiday_tag({"pos": "WR"}, [], d, "DAL", "Cowboys") is None
