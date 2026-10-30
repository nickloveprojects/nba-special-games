from datetime import date

from app import nba_projection as npj

TODAY = date(2026, 10, 29)


def g(d, tm="MEM", **r):
    base = {"date": d, "tm": tm, "min": 30, "pts": 20, "reb": 5, "ast": 4, "playoff": False}
    return {**base, **r}


LOGS = [g(f"2026-10-{d:02d}") for d in (2, 5, 8, 11, 14, 17, 20, 23, 26)]
TABLE = {f"T{i}": {"n": 10, "ALL": {"pts": 100.0 + i, "reb": 40.0, "ast": 24.0}} for i in range(12)}


def test_steady_player_projects_to_his_line_with_a_range():
    p = npj.project(LOGS, "MEM", {}, TODAY, 1)
    pts, reb, ast = p["lines"]
    assert pts["proj"] == 20 and reb["proj"] == 5 and ast["proj"] == 4 and p["minutes"] == 30
    assert pts["lo"] <= pts["proj"] <= pts["hi"]


def test_more_minutes_lately_raises_projection():
    up = LOGS[:5] + [g(f"2026-10-{d:02d}", min=36, pts=24) for d in (20, 23, 26)]
    assert npj.project(up, "MEM", {}, TODAY, 1)["lines"][0]["proj"] > 20


def test_hot_week_is_pulled_back_toward_his_normal_rate():
    hot = [g(f"2026-10-{d:02d}", pts=40) for d in (23, 26)] + LOGS[:7]
    assert 20 < npj.project(hot, "MEM", {}, TODAY, 1)["lines"][0]["proj"] < 40


def test_minutes_come_from_current_team_but_rate_travels():
    other = [g(f"2026-09-{d:02d}", tm="LAL", min=20, pts=20) for d in (3, 6, 9, 12, 15, 18)]   # 1.0 pts a minute
    mine = [g(f"2026-10-{d:02d}", min=30, pts=30) for d in (20, 23, 26)]                       # 1.0 pts a minute
    p = npj.project(other + mine, "MEM", {}, TODAY, 1)
    assert p["minutes"] == 30 and p["games_used"] == 3 and p["lines"][0]["proj"] == 30
    assert npj.project(other, "MEM", {}, TODAY, 1) is None            # no games with the new team yet
    assert npj.project(other + mine[:2], "MEM", {}, TODAY, 1) is None  # needs three
    po = [g(f"2026-10-{d:02d}", playoff=True) for d in (3, 6, 9, 12, 15, 18)]
    assert npj.project(po, "MEM", {}, TODAY, 1) is None


def test_today_game_ignored_and_too_few_or_low_minutes_get_none():
    assert npj.project(LOGS + [g("2026-10-29", pts=60)], "MEM", {}, TODAY, 1)["lines"][0]["proj"] == 20
    assert npj.project(LOGS[:2], "MEM", {}, TODAY, 1) is None
    bench = [g(f"2026-10-{d:02d}", min=6, pts=2) for d in (2, 5, 8, 11, 14, 17)]
    assert npj.project(bench, "MEM", {}, TODAY, 1) is None
    assert npj.project(LOGS, "MEM", {}, TODAY, 1, status="Out") is None


def test_opponent_factors_are_softened_and_clamped():
    f = npj.opp_factors(TABLE, "T11")
    assert 1.0 < f["pts"] <= 1.12 and f["reb"] == 1.0
    assert npj.opp_factors(TABLE, "T0")["pts"] < 1.0
    assert npj.opp_factors({}, "X") == {"pts": 1.0, "reb": 1.0, "ast": 1.0}
    hi = npj.project(LOGS, "MEM", npj.opp_factors(TABLE, "T11"), TODAY, 1)["lines"][0]["proj"]
    base = npj.project(LOGS, "MEM", npj.opp_factors({}, "X"), TODAY, 1)["lines"][0]["proj"]
    assert hi >= base                       # a generous defense never lowers the projection


def test_this_season_leads_and_old_data_cannot_carry_a_projection():
    from datetime import date as d
    def g(day, pts, tm="PHI"):
        return {"date": day, "tm": tm, "min": 34, "pts": pts, "reb": 8, "ast": 3, "playoff": False}
    old = [g(f"2026-0{1 + i % 4}-{10 + i:02d}", 32) for i in range(15)]
    new = [g(f"2026-10-{20 + i}", 20) for i in range(4)]
    today = d(2026, 10, 30)
    p = npj.project(old + new, "PHI", {}, today, 1)
    assert p and p["games_used"] == 4 and p["lines"][0]["proj"] < 27     # last season's 32s only pull it up a little
    assert npj.project(old + new[:2], "PHI", {}, today, 1) is None       # only 2 games this season: no number
    assert npj.project(old + [g("2026-10-25", 20, "NYK")] * 4, "PHI", {}, today, 1) is None   # games for another club do not count
