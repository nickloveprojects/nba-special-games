from datetime import date, datetime, timezone

from app import projection as pj

TODAY = date(2026, 10, 30)


def g(d, **r):
    return {"date": d, "post": False, "row": r}


LOGS = [g(f"2026-10-{d:02d}", receptions=6, receivingTargets=9, receivingYards=80) for d in (2, 9, 16, 23)]
TABLE = {f"T{i}": {"WR": {"rec_yds": 100.0 + i, "rec": 10.0}} for i in range(10)}


def test_projection_tracks_recent_games_and_range_brackets_it():
    p = pj.project("WR", LOGS, {}, "X", TODAY, 1, "")
    rec, yds = p["lines"]
    assert 5.5 <= rec["proj"] <= 6.1 and 74 <= yds["proj"] <= 82 and yds["lo"] <= yds["proj"] <= yds["hi"]
    assert p["games_used"] == 4


def test_same_seed_same_answer():
    assert pj.project("WR", LOGS, {}, "X", TODAY, 5, "") == pj.project("WR", LOGS, {}, "X", TODAY, 5, "")


def test_weak_defense_raises_and_strong_defense_lowers():
    weak = pj.project("WR", LOGS, TABLE, "T9", TODAY, 1, "")["lines"][1]["proj"]
    strong = pj.project("WR", LOGS, TABLE, "T0", TODAY, 1, "")["lines"][1]["proj"]
    assert strong < weak


def test_opponent_effect_is_clamped():
    t = {f"T{i}": {"WR": {"rec_yds": 100.0, "rec": 10.0}} for i in range(9)}
    t["BAD"] = {"WR": {"rec_yds": 900.0, "rec": 10.0}}
    assert pj.opp_factor(t, "BAD", "WR", "rec_yds") == pj.OPP_CLAMP[1]


def test_too_few_games_or_out_players_get_nothing():
    assert pj.project("WR", LOGS[:2], {}, "X", TODAY, 1, "") is None
    assert pj.project("WR", LOGS, {}, "X", TODAY, 1, "Out") is None
    assert pj.project("WR", LOGS, {}, "X", TODAY, 1, "Doubtful") is None
    assert pj.project("WR", LOGS, {}, "X", TODAY, 1, "Questionable") is not None
    assert pj.project("K", LOGS, {}, "X", TODAY, 1, "") is None


def test_old_games_and_todays_game_are_ignored():
    old = [g("2024-01-01", receptions=20, receivingTargets=25, receivingYards=300)] * 5
    assert pj.project("WR", old, {}, "X", TODAY, 1, "") is None
    today_game = LOGS + [g("2026-10-30", receptions=50, receivingTargets=60, receivingYards=900)]
    assert pj.project("WR", today_game, {}, "X", TODAY, 1, "")["lines"][1]["proj"] < 90


def test_only_games_with_current_team_count():
    other = [dict(x, team_id=11) for x in LOGS]
    mine = [dict(g(f"2026-10-{d:02d}", receptions=2, receivingTargets=3, receivingYards=20), team_id=30) for d in (3, 10, 17)]
    p = pj.project("WR", other + mine, {}, "X", TODAY, 1, "", team_id=30)
    assert p["games_used"] == 3 and p["lines"][1]["proj"] < 40
    assert pj.project("WR", other, {}, "X", TODAY, 1, "", team_id=30) is None


def test_negligible_role_gets_no_projection():
    bench = [dict(g(f"2026-10-{d:02d}", rushingAttempts=0, receivingTargets=0), team_id=1) for d in (2, 9, 16, 23)]
    assert pj.project("RB", bench, {}, "X", TODAY, 1, "", team_id=1) is None


def test_freeze_locks_after_kickoff():
    before = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
    after = datetime(2026, 10, 30, 21, tzinfo=timezone.utc)
    tip = "2026-10-30T20:15:00+00:00"
    fresh, old = {"lines": [1]}, {"lines": [2]}
    assert pj.freeze(fresh, old, tip, before) == {"lines": [1], "locked": False}
    assert pj.freeze(None, old, tip, after) == {"lines": [2], "locked": True}
    assert pj.freeze(None, None, tip, after) is None


def test_yardage_range_is_wider_than_raw_spread():
    mixed = [g(f"2026-10-{d:02d}", receptions=r, receivingTargets=r + 2, receivingYards=y) for d, r, y in ((2, 3, 30), (9, 8, 110), (16, 5, 60), (23, 7, 95))]
    p = pj.project("WR", mixed, {}, "X", TODAY, 3, "")
    yds = p["lines"][1]
    assert yds["lo"] <= 30 and yds["hi"] >= 110


def test_lucky_efficiency_is_pulled_toward_league_norm():
    lucky = [g(f"2026-10-{d:02d}", receptions=3, receivingTargets=3, receivingYards=60) for d in (2, 9, 16, 23)]  # 20 yds/target
    p = pj.project("WR", lucky, {}, "X", TODAY, 1, "")
    assert 3 * 7.95 < p["lines"][1]["proj"] < 60
