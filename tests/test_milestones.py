from app import milestones as m

LISTS = {
    "fgm": {"label": "field goals made", "short": "FGM", "source": {"label": "src", "url": "http://x"},
            "rows": [{"name": "A One", "total": 15000}, {"name": "B Two", "total": 11330},
                     {"name": "Kevin Durant", "total": 11000, "espn_id": 1}, {"name": "C Three", "total": 10000}]},
}


def test_passing_next_player_uses_live_total_for_active_rows():
    live = {1: {"fgm": 11328}}
    tags = m.tags_for("Kevin Durant", {"fgm": 11328}, LISTS, fetch=lambda i: live.get(i))
    assert tags[0]["headline"].startswith("Needs 3 FGM to pass B Two for 2nd")


def test_too_far_away_gives_no_flag():
    assert m.tags_for("Kevin Durant", {"fgm": 11000}, LISTS, fetch=lambda i: None) == []


def test_round_number_and_entering_the_list():
    t = m.tags_for("New Guy", {"fgm": 9990}, LISTS, fetch=lambda i: None)
    kinds = {x["kind"]: x["headline"] for x in t}
    assert "to reach 10,000 career field goals made" in kinds["round"]
    assert "enter the all-time top 4" in kinds["rank"] or "pass C Three" in kinds["rank"]


def test_no_totals_no_flags():
    assert m.tags_for("Nobody", None, LISTS) == []


def test_parse_totals_and_ordinal():
    d = {"categories": [{"name": "totals", "labels": ["FG", "PTS"], "totals": ["11328-22516", "32828"]}]}
    assert m.parse_totals(d) == {"fgm": 11328, "pts": 32828}
    assert [m.ordinal(n) for n in (1, 2, 3, 7, 11, 22)] == ["1st", "2nd", "3rd", "7th", "11th", "22nd"]
