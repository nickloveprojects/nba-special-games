from datetime import date

from app import career


def g(d, opp="BOS", venue="BOS", pts=20, reb=5, ast=3):
    return {"date": d, "opp": opp, "venue": venue, "pts": pts, "reb": reb, "ast": ast, "home": False, "result": "W", "gid": d}


def test_holidays():
    assert career.holiday_name(date(2026, 12, 25)) == "Christmas"
    assert career.holiday_name(date(2027, 1, 18)) == "MLK Day"      # third Monday of January 2027
    assert career.holiday_name(date(2026, 10, 30)) is None


def test_lines_only_real_data():
    logs = [g("2024-03-12", pts=30), g("2025-03-12", pts=20), g("2025-12-25", pts=10), g("2025-01-01", venue="NYK", pts=8)]
    tags = [{"category": "Birthday"}, {"category": "Hometown", "_place": (40.75, -73.99)},
            {"category": "Revenge", "_exit": "2025-06-01"}]
    out = career.lines(logs, date(2026, 3, 12), date(1999, 3, 12), tags, "BOS", "Celtics")
    by = {x["kind"]: x for x in out}
    assert by["birthday"]["n"] == 2 and by["birthday"]["pts"] == 25.0 and "2 times" in by["birthday"]["text"]
    assert by["hometown"]["n"] == 1 and "hometown area 1 time" in by["hometown"]["text"]      # only the game in New York
    assert by["revenge"]["n"] == 1 and "since leaving" in by["revenge"]["text"]   # only the 2025-12-25 game is after the exit
    assert "holiday" not in by
    xmas = career.lines(logs, date(2026, 12, 25), date(1999, 3, 12), [], "BOS", "Celtics")
    assert xmas[0]["kind"] == "holiday" and xmas[0]["n"] == 1 and "Christmas" in xmas[0]["text"]


def test_history_line_from_h2h_and_nothing_when_empty():
    t = {"category": "History", "with": "Tyler Herro", "h2h": {"games": 5, "scope": "x", "me": {"pts": 14.4, "reb": 9.0, "ast": 3.8}}}
    out = career.lines([], date(2026, 10, 28), None, [t], "MIL", "Bucks")
    assert out[0]["text"] == "Has faced Tyler Herro 5 times (avg 14.4 pts, 9.0 reb, 3.8 ast)."
    t["h2h"]["games"] = 0
    assert career.lines([], date(2026, 10, 28), None, [t], "MIL", "Bucks") == []
