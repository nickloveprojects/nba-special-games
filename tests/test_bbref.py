from app.sources import bbref

PLAYER_PAGE = """
<div><p><strong>
      High School:
    </strong>
      DeMatha Catholic in Hyattsville, <a href='/friv/high_schools.fcgi?country=US&state=MD'>Maryland</a>
  </p></div>
<!-- <div class="section_content" id="div_transactions">
<span class=' nba-transactions'><p class="transaction "><strong>June 26, 2014</strong>: Drafted by the <a data-attr-to="PHI" href="/teams/PHI/2014.html">Philadelphia 76ers</a> in the 2nd round (39th pick) of the 2014 NBA Draft.</p></span>
<span class=' nba-transactions'><p class="transaction "><strong>September 6, 2021</strong>: Waived by the <a data-attr-from="DET" href="/teams/DET/2022.html">Detroit Pistons</a>. $4M buyout</p></span>
<span class=' nba-transactions'><p class="transaction "><strong>June 29, 2026</strong>: Traded by the <a data-attr-from="POR" href="/teams/POR/2026.html">Portland Trail Blazers</a> with <a href="/players/m/murrakr01.html">Kris Murray</a> to the <a data-attr-to="MEM" href="/teams/MEM/2026.html">Memphis Grizzlies</a> for <a href="/players/m/moranja01.html">Ja Morant</a> and cash.</p></span>
<span class=' nba-transactions'><p class="transaction "><strong>November 2, 2021</strong>: Assigned to the <a href="/x">Santa Cruz Warriors</a> of the G-League.</p></span>
<span class=' nba-transactions'><p class="transaction "><strong>August 7, 2021</strong>: Signed a contract extension with the <a data-attr-to="MIA" href="/teams/MIA/2022.html">Miami Heat</a>.</p></span>
</div> -->
"""

INDEX = """<tr ><th scope="row" class="left " data-append-csv="grantje01" data-stat="player" ><strong><a href="/players/g/grantje01.html">Jerami Grant</a></strong></th><td class="right " data-stat="year_min" >2015</td><td class="right " data-stat="year_max" >2027</td><td class="left " data-stat="birth_date" csk="19940312" ><a href="x">March 12, 1994</a></td></tr>
<tr ><th scope="row" class="left " data-append-csv="grantje02" data-stat="player" ><a href="/players/g/grantje02.html">Jerian Grant</a></th><td class="right " data-stat="year_max" >2020</td><td class="left " data-stat="birth_date" csk="19920930" >x</td></tr>"""


def test_parse_player_reads_high_school_and_transactions():
    d = bbref.parse_player(PLAYER_PAGE)
    assert d["high_schools"] == [{"school": "DeMatha Catholic", "city": "Hyattsville", "region": "Maryland"}]
    kinds = [(t["kind"], t["teams"]) for t in d["transactions"]]
    assert kinds == [("draft", ["PHI"]), ("waive", ["DET"]), ("trade", ["POR", "MEM"])]   # G-League + extension skipped
    assert d["transactions"][2]["date"] == "2026-06-29"


def test_parse_hs_variants():
    assert bbref.parse_hs("Oak Hill Academy in Mouth of Wilson, Virginia")[0]["city"] == "Mouth of Wilson"
    two = bbref.parse_hs("Findlay Prep in Henderson, Nevada and Hillcrest in Dallas, Texas")
    assert [x["city"] for x in two] == ["Henderson", "Dallas"]
    assert bbref.parse_hs("") == []


def test_parse_index_and_find_slug(tmp_path):
    from datetime import date

    from app import db
    rows = bbref.parse_index(INDEX)
    assert rows[0] == {"slug": "grantje01", "name": "Jerami Grant", "year_max": 2027, "birth": "1994-03-12"}
    conn = db.connect()
    for r in rows:
        conn.execute("INSERT OR REPLACE INTO bbref_index VALUES(?,?,?,?,?)", (r["slug"], r["name"], r["birth"], r["year_max"], "g"))
    conn.execute("INSERT OR REPLACE INTO bbref_letters VALUES('g', datetime('now'))")
    conn.commit()
    assert bbref.find_slug(conn, "Jerami Grant", date(1994, 3, 12)) == "grantje01"
    assert bbref.find_slug(conn, "Jerami Grant", date(1999, 1, 1)) is None     # birth date mismatch = someone else
