# Beef candidates — run of 2026-11-06

Games checked: NBA Nov 6-7 (16 games), NFL Nov 8-9 (14 games). Nothing here has been added to config/rivalries.yaml or config/rivalries_nfl.yaml. Paste a block only after approval.

## 1. Kevin Durant vs. Dillon Brooks
- Game: Rockets at Suns, Sat Nov 7, 2026 (9:00 PM ET). Both are on the game's entries (Durant HOU, Brooks PHX).
- Kind: Altercation
- Reason (as the articles state): Brooks was ejected in the Rockets-Suns game on March 30, 2025 after a scuffle with Durant (technicals went to both). In the April 7, 2026 rematch, Durant crossed Brooks over to the floor and said "He's not that much of a concern to me."
- Sources:
  - Pro Football & Sports Network, Mar 31, 2025: https://www.profootballnetwork.com/nba/dillon-brooks-ejected-kevin-durant/
  - Sports Illustrated (Phoenix Suns On SI), Apr 8, 2026: https://www.si.com/nba/suns/onsi/news/kevin-durant-fires-back-dillon-brooks-antics
  - Sports Illustrated (Houston Rockets On SI), Apr 9, 2026: https://www.si.com/nba/rockets/onsi/news/watch-rockets-get-into-multiple-scuffles-with-suns-as-former-players-clash

```yaml
  - players: ["Dillon Brooks", "Kevin Durant"]
    kind: Altercation
    date: "2025-03-30"
    reason: "Brooks was ejected after a scuffle with Durant in a Rockets-Suns game on March 30, 2025; both players received technical fouls."
    sources:
      - {label: "Pro Football & Sports Network", url: "https://www.profootballnetwork.com/nba/dillon-brooks-ejected-kevin-durant/"}
      - {label: "Sports Illustrated", url: "https://www.si.com/nba/suns/onsi/news/kevin-durant-fires-back-dillon-brooks-antics"}
```
Note: the Oct 2026 Brooks Instagram jab ("stench in the locker room") was aimed at the Suns' past, not named at Durant in the article; left out of the reason. The "My worst is better than your best" quote comes from lip readers and is unconfirmed; left out.

## 2. Stephon Castle vs. Deni Avdija
- Game: Spurs at Trail Blazers, Sat Nov 7, 2026 (10:00 PM ET).
- Kind: Altercation
- Reason (as the articles state): Late in Game 4 of the 2026 first-round series (April 26, 2026), Avdija and Castle shoved each other after Castle pushed the ball into Avdija's chest following an and-one, and both got offsetting technical fouls. Avdija said, "there's a level of disrespect that I'm not gonna accept."
- Sources:
  - Eurohoops, Apr 27, 2026: https://www.eurohoops.net/en/nba-news/1960820/deni-avdija-talks-portland-trail-blazers-loss-versus-san-antonio-spurs-game-4-nba-playoffs/
  - Sports Illustrated (Spurs On SI), Apr 27, 2026: https://www.si.com/nba/spurs/onsi/just-disrespectful-how-stephon-castle-got-under-deni-avdija-s-skin-as-spurs-beat-blazers

```yaml
  - players: ["Stephon Castle", "Deni Avdija"]
    kind: Altercation
    date: "2026-04-26"
    reason: "Avdija and Castle shoved each other late in Game 4 of the 2026 Spurs-Trail Blazers series (April 26, 2026) and received offsetting technical fouls; Avdija said Castle's actions were disrespectful."
    sources:
      - {label: "Eurohoops", url: "https://www.eurohoops.net/en/nba-news/1960820/deni-avdija-talks-portland-trail-blazers-loss-versus-san-antonio-spurs-game-4-nba-playoffs/"}
      - {label: "Sports Illustrated", url: "https://www.si.com/nba/spurs/onsi/just-disrespectful-how-stephon-castle-got-under-deni-avdija-s-skin-as-spurs-beat-blazers"}
```
Caveats: the technicals are in Eurohoops and SI but not in Hoops Rumors or Heavy (neither says otherwise). SI says Avdija fouled out; Eurohoops does not, so that is left out. Castle and Avdija are not in the game's entries file, so confirm both are still on the Spurs/Blazers (rosters not independently checked this run).

## Could not verify
- Stefon Diggs vs. Keisean Nixon (Packers at Patriots, Nov 8): Fox Sports/AP (Oct 20, 2024) confirms a pregame scuffle with Diggs, Jaire Alexander and Nixon. I could not confirm that Diggs or Nixon is on the Patriots/Packers now (the Patriots team page did not list Diggs), so it is not proposed. Nixon is already paired with Michael Wilson in rivalries_nfl.yaml.
- Search snippets only, not fetched or not tied to a listed game: Celtics-Hornets 2024 ejections (Nov 1, 2024), Eagles-Commanders brawl Dec 2025 (not on this week's schedule), Mitchell/Knicks trash talk (no named Knicks-Cavs player pair confirmed).
- Coverage was search-based for NBA games and a few NFL games; not every NFL matchup (CIN-ATL, DAL-IND, NYJ-KC, DET-MIA, CLE-NO, NYG-PHI, LAR-WSH, DEN-CAR, HOU-LAC, BUF-MIN) produced a confirmable two-player item.
