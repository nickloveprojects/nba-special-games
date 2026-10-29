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


def test_find_exit_only_uses_real_transactions():
    rows = [{"date": "2026-10-12", "team": "ARI", "name": "Arizona Cardinals",
             "text": "Traded WR Marvin Harrison Jr. and a 2027 sixth-round draft pick to Houston for picks. Signed K A B."},
            {"date": "2026-10-13", "team": "HOU", "name": "Houston Texans", "text": "Acquired WR Someone Else from Arizona."}]
    ex = feed.find_exit(rows, "Marvin Harrison Jr.", "ARI", "Arizona Cardinals", "HOU")
    assert ex["kind"] == "trade" and ex["date"] == "2026-10-12" and ex["text"].startswith("Traded WR Marvin")
    assert feed.find_exit(rows, "Nobody Here", "ARI", "Arizona Cardinals", "HOU") is None


def test_revenge_needs_real_games_with_the_team():
    opp = {"id": 7, "abbr": "DEN", "short": "Broncos", "name": "Denver Broncos"}
    few = [dict(LOG(), team_id=7, season=2024)] * 3
    assert nfl.revenge_tag({"name": "X"}, opp, few, [], "KC") is None
    many = [dict(LOG(), team_id=7, season=2023)] * 4 + [dict(LOG(), team_id=7, season=2025)] * 4
    t = nfl.revenge_tag({"name": "X"}, opp, many, [], "KC")
    assert t["kind"] == "unknown" and t["confidence"] == "low" and "2023 to 2025 (8 games)" in t["how_left"]


def test_holiday_tag_uses_only_past_holiday_games():
    d = date(2026, 11, 26)    # Thanksgiving
    past = dict(LOG(receptions=5, receivingYards=60, receivingTouchdowns=1), date="2024-11-28", opp="DAL")
    t = nfl.holiday_tag({"pos": "WR"}, [past], d, "DAL", "Cowboys")
    assert t["label"] == "Thanksgiving" and "1 time" in t["lines"][0]["text"] and len(t["lines"]) == 3
    assert nfl.holiday_tag({"pos": "WR"}, [], d, "DAL", "Cowboys") is None
