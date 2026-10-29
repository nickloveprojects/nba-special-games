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


def test_history_line_from_h2h_and_nothing_when_empty():
    t = {"category": "History", "with": "Tyler Herro", "h2h": {"games": 5, "scope": "x", "me": {"pts": 14.4, "reb": 9.0, "ast": 3.8}}}
    out = career.lines([], date(2026, 10, 28), None, [t], "MIL", "Bucks")
    assert out[0]["text"] == "Has faced Tyler Herro 5 times (avg 14.4 pts, 9.0 reb, 3.8 ast)."
    t["h2h"]["games"] = 0
    assert career.lines([], date(2026, 10, 28), None, [t], "MIL", "Bucks") == []


def test_holiday_tag():
    logs = [g("2025-12-25", opp="BOS", pts=10), g("2024-12-25", opp="NYK", pts=20), g("2025-02-01", opp="BOS", pts=30)]
    t = career.holiday_tag(logs, date(2026, 12, 25), "BOS", "Celtics")
    assert t["category"] == "Holiday" and t["label"] == "Christmas" and t["headline"] == "Christmas game."
    texts = [x["text"] for x in t["lines"]]
    assert texts[0].startswith("Has played on Christmas 2 times (avg 15.0 pts")
    assert texts[1].startswith("Has faced the Celtics 2 times in his career (avg 20.0 pts")
    assert texts[2].startswith("On Christmas against the Celtics: 1 time")
    assert career.holiday_tag([g("2025-02-01")], date(2026, 12, 25), "BOS", "Celtics") is None   # never played on a holiday
    assert career.holiday_tag(logs, date(2026, 12, 24), "BOS", "Celtics") is None                # not a holiday
