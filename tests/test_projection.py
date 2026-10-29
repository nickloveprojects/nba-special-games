from datetime import date, datetime, timezone

from app import projection as pj

TODAY = date(2026, 10, 30)


def g(d, **r):
    return {"date": d, "post": False, "row": r}


LOGS = [g(f"2026-10-{d:02d}", receptions=6, receivingYards=80, receivingTouchdowns=0) for d in (2, 9, 16, 23)]
TABLE = {f"T{i}": {"WR": {"rec_yds": 100.0 + i, "rec": 10.0}} for i in range(10)}


def test_projection_tracks_recent_games_and_range_brackets_it():
    p = pj.project("WR", LOGS, {}, "X", TODAY, 1, "")
    rec, yds = p["lines"]
    assert rec["proj"] == 6 and yds["proj"] == 80 and yds["lo"] <= 80 <= yds["hi"]
    assert p["games_used"] == 4 and p["td_prob"] == 0


def test_same_seed_same_answer():
    assert pj.project("WR", LOGS, {}, "X", TODAY, 5, "") == pj.project("WR", LOGS, {}, "X", TODAY, 5, "")


def test_weak_defense_raises_and_strong_defense_lowers():
    weak = pj.project("WR", LOGS, TABLE, "T9", TODAY, 1, "")["lines"][1]["proj"]
    strong = pj.project("WR", LOGS, TABLE, "T0", TODAY, 1, "")["lines"][1]["proj"]
    assert strong < 80 < weak


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
    old = [g("2024-01-01", receptions=20, receivingYards=300)] * 5
    assert pj.project("WR", old, {}, "X", TODAY, 1, "") is None
    today_game = LOGS + [g("2026-10-30", receptions=50, receivingYards=900)]
    assert pj.project("WR", today_game, {}, "X", TODAY, 1, "")["lines"][1]["proj"] == 80


def test_td_probability_from_scoring_history():
    scorer = [g(f"2026-10-{d:02d}", receptions=5, receivingYards=60, receivingTouchdowns=1) for d in (2, 9, 16, 23)]
    assert pj.project("WR", scorer, {}, "X", TODAY, 1, "")["td_prob"] > 55


def test_freeze_locks_after_kickoff():
    before = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
    after = datetime(2026, 10, 30, 21, tzinfo=timezone.utc)
    tip = "2026-10-30T20:15:00+00:00"
    fresh, old = {"lines": [1]}, {"lines": [2]}
    assert pj.freeze(fresh, old, tip, before) == {"lines": [1], "locked": False}
    assert pj.freeze(None, old, tip, after) == {"lines": [2], "locked": True}
    assert pj.freeze(None, None, tip, after) is None
