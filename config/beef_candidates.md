# Beef candidates — run of 2026-11-15
Games covered: NBA and NFL games on 2026-11-15 and 2026-11-16 (see web/data). Nothing here has been added to config/rivalries.yaml or config/rivalries_nfl.yaml; paste only what you approve.

**Roster caveat for both items:** I could not load ESPN roster pages in this run, so I did NOT confirm that these four players are still on the teams listed. The app only shows a History box when both players are on the two teams that day, so a wrong roster is harmless but check before approving.

## 1. Jalen Ramsey vs. Ja'Marr Chase — Steelers at Bengals, 2026-11-15 (8:20 PM ET)
- Kind: Altercation
- Reason: Ramsey was ejected for throwing a punch at Chase in the Steelers-Bengals game on Nov. 16, 2025; Ramsey said Chase spat on him, and Chase was suspended one game.
- What the articles say: SI's Pittsburgh Steelers On SI (Nov. 24 and Nov. 27, 2025) report the two were face to face before Ramsey took a swing, both got offsetting unsportsmanlike penalties, only Ramsey was ejected, Ramsey said Chase spat after the game, and Chase was suspended for the following week. TribLive reports referee Bill Vinovich said Ramsey was ejected for a punch and no official saw a spit.
- Unverified: the CBS Sports article could not be fetched, so it is not cited. The two SI articles disagree on whether Chase was also fined (Nov. 24 says "fined and suspended for one game"; Nov. 27 says only suspended). The reason line above avoids the fine. TribLive's page showed no publish date (its embedded posts are dated Nov. 16, 2025).
- Sources: https://www.si.com/nfl/steelers/onsi/news/bengals-jamarr-chase-apologizes-pittsburgh-steelers ; https://www.si.com/nfl/steelers/onsi/news/jamarr-chase-throws-shade-pittsburgh-steelers-jalen-ramsey ; https://triblive.com/sports/jamarr-chases-apparent-spit-toward-jalen-ramsey-stokes-steelers-bengals-rivalry

```yaml
  - players: ["Jalen Ramsey", "Ja'Marr Chase"]
    kind: Altercation
    date: "2025-11-16"
    reason: "Ramsey was ejected for throwing a punch at Chase in the Steelers-Bengals game on Nov. 16, 2025; Ramsey said Chase spat on him, and Chase was suspended one game."
    sources:
      - {label: "Steelers On SI", url: "https://www.si.com/nfl/steelers/onsi/news/bengals-jamarr-chase-apologizes-pittsburgh-steelers"}
      - {label: "Steelers On SI", url: "https://www.si.com/nfl/steelers/onsi/news/jamarr-chase-throws-shade-pittsburgh-steelers-jalen-ramsey"}
      - {label: "TribLive", url: "https://triblive.com/sports/jamarr-chases-apparent-spit-toward-jalen-ramsey-stokes-steelers-bengals-rivalry"}
```

## 2. Kevin Durant vs. Tyler Herro — Rockets at Heat, 2026-11-16 (7:30 PM ET)
- Kind: Feud
- Reason: Durant and Herro each got a technical foul after exchanging words in the first quarter of the Rockets-Heat game in Miami on Feb. 28, 2026 (Heat won 115-105).
- What the articles say: Larry Brown Sports (Feb. 28, 2026) says both got technicals, they had to be separated, and it wasn't clear what started it. SI (Mar. 1, 2026) says Herro said Durant told him he couldn't guard him, and the two shared a dap after the game. No ejections or fines are mentioned.
- Unverified: neither article prints the calendar date of the game; I took Feb. 28, 2026 (a Saturday) from the publish date and the "Saturday's game" wording. Other results (leaked video, "burner account" jabs) came from snippets only and were not read, so they are not used.
- Sources: https://larrybrownsports.com/basketball/kevin-durant-tyler-herro-heated-exchange/743509 ; https://www.si.com/nba/heat/tyler-herro-explains-why-he-exchanged-words-with-kevin-durant-rockets-heat-game

```yaml
  - players: ["Kevin Durant", "Tyler Herro"]
    kind: Feud
    date: "2026-02-28"
    reason: "Durant and Herro each received a technical foul after exchanging words in the first quarter of the Rockets-Heat game in Miami on Feb. 28, 2026."
    sources:
      - {label: "Larry Brown Sports", url: "https://larrybrownsports.com/basketball/kevin-durant-tyler-herro-heated-exchange/743509"}
      - {label: "Sports Illustrated", url: "https://www.si.com/nba/heat/tyler-herro-explains-why-he-exchanged-words-with-kevin-durant-rockets-heat-game"}
```

## Skipped / not usable
- LeBron James vs. Dillon Brooks (LAL at PHX, Nov. 15): already in rivalries.yaml.
- Amen Thompson vs. Tyler Herro: already listed. Brooks/Durant and Jalen Green/Amen Thompson (SI, Apr. 9, 2026) involve players not on the same teams in this window's games, so they do not apply.
- Kris Dunn / Luka Doncic / Jaxson Hayes (Eurohoops, Nov. 26, 2025): Doncic and Dunn are on LAL/LAC, which do not play each other in this window.
- Dec. 2024 Heat-Rockets fight (Cebu Daily News) and the SAN suspension article: the SAN link redirected to its homepage and was not read.

## Coverage gaps (be aware)
Searches this run were broad, not one per game. Games with no dedicated search and no candidate found: IND@PHI, CHA@LAC, SAS@UTA, DAL@BOS, NYK@TOR, ATL@MIL, OKC@SAC, ORL@BOS, CHI@CLE, MEM@WAS, PHI@BKN, POR@MIN, GSW@NOP, PHX@DEN; NFL NE@DET, KC@ATL, HOU@CLE, MIN@GB, JAX@TEN, MIA@IND, CAR@NO, BUF@NYJ, SEA@LV, LAR@ARI, SF@DAL, LAC@BAL. The Knicks-Raptors search turned up nothing confirmable. "No new candidates" for those games means none were confirmed, not that none exist.
