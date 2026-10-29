from app import matchups


def _box(a, b, ga, gb):
    row = lambda pos, pts, reb, ast: {"athlete": {"position": {"abbreviation": pos}}, "stats": [str(pts), str(reb), str(ast)]}  # noqa: E731
    mk = lambda ab, rows: {"team": {"abbreviation": ab}, "statistics": [{"names": ["PTS", "REB", "AST"], "athletes": rows}]}  # noqa: E731
    return {"boxscore": {"players": [mk(a, [row(*r) for r in ga]), mk(b, [row(*r) for r in gb])]}}


def test_parse_and_table():
    box = matchups.parse_box(_box("NY", "PHI", [("PG", 20, 3, 8), ("C", 10, 12, 1)], [("SG", 30, 2, 5)]))
    assert box["NYK"]["G"]["pts"] == 20 and box["NYK"]["C"]["reb"] == 12 and box["NYK"]["opp"] == "PHI"
    table = matchups.build_table([box])
    assert table["PHI"]["G"]["pts"] == 20 and table["PHI"]["ALL"]["reb"] == 15 and table["NYK"]["G"]["pts"] == 30


def test_matchup_grade_and_dnp():
    boxes = [matchups.parse_box(_box("NY", "PHI", [("PG", 40, 3, 8)], [("SG", 10, 2, 5)])),
             matchups.parse_box(_box("BOS", "CHI", [("PG", 20, 3, 8)], [("SG", 25, 2, 5)]))]
    table = matchups.build_table(boxes)
    m = matchups.matchup(table, "PHI", "PG")                  # PHI gave up 40 to a guard: the most of 4 teams
    assert m["group"] == "G" and m["stats"]["pts"]["rank"] == 1 and m["stats"]["pts"]["color"] == "green"
    assert matchups.matchup(table, "ATL", "PG") is None       # no games yet
    low = matchups.matchup(table, "NYK", "PG")                # NYK gave up only 10
    assert low["stats"]["pts"]["color"] in ("red", "yellow") and low["grade"] in "CDF"
    dnp = _box("NY", "PHI", [("PG", 5, 1, 1)], [("SG", 5, 1, 1)])
    dnp["boxscore"]["players"][0]["statistics"][0]["athletes"].append({"didNotPlay": True, "stats": [], "athlete": {}})
    assert matchups.parse_box(dnp)["NYK"]["G"]["pts"] == 5
