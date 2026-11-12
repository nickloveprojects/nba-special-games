# Beef candidates (review needed)

Generated 2026-11-12 by the beef-review routine. Window: NBA games on Nov 12-14, 2026 (web/data/2026-11-12.json, 2026-11-13.json). Nothing here has been added to config/rivalries.yaml; paste a YAML block only if you approve it. Facts below are limited to what the fetched articles state.

## 1. Draymond Green vs. Victor Wembanyama

- Game: Warriors @ Spurs, Nov 14, 2026 (listed in the Nov 13 data file as GSW-SAS)
- Kind: Feud
- Reason: In a Friday-night Warriors-Spurs game in November 2025, Green and Wembanyama exchanged words before an inbounds play, Wembanyama dunked over Green (waved off for a foul on Green), and Green later described the exchange on his podcast.
- Sources: ESPN, Nov 18, 2025 (https://africa.espn.com/nba/story/_/id/47005045/draymond-green-victor-wembanyama-alley-oop-dunk-spurs-warriors); Sports Illustrated, Nov 17, 2025 (https://www.si.com/nba/warriors/onsi/news/draymond-green-reveals-trash-talk-he-used-on-wemby-before-getting-dunked-on-01kaa270x4qv); CBS Sports, Nov 15, 2025 (https://www.cbssports.com/nba/news/victor-wembanyama-dunk-draymond-green-trash-talk)
- Caveats: ESPN says Green blocked Wembanyama just before the exchange, SI says the exchange came right before the inbound; the YAML reason avoids that detail. CBS's page was only partly read verbatim, so it is a supporting link, not a basis for the claim. A Bleacher Report piece (Jun 13, 2026) has Green calling Wembanyama's tactics "a bit dirty" but it is a general remark about European players and is not used. I did not confirm that both players are on these teams for 2026-27 from a roster source.

```yaml
  - players: ["Draymond Green", "Victor Wembanyama"]
    kind: Feud
    date: "2025-11"
    reason: "In a Warriors-Spurs game in November 2025, Green and Wembanyama exchanged words before an inbounds play and Wembanyama dunked over him (the basket was waved off for a foul on Green); Green later described the exchange on his podcast."
    sources:
      - {label: "ESPN", url: "https://africa.espn.com/nba/story/_/id/47005045/draymond-green-victor-wembanyama-alley-oop-dunk-spurs-warriors"}
      - {label: "Sports Illustrated", url: "https://www.si.com/nba/warriors/onsi/news/draymond-green-reveals-trash-talk-he-used-on-wemby-before-getting-dunked-on-01kaa270x4qv"}
```

## 2. Trae Young vs. Daniss Jenkins

- Game: Pistons @ Wizards, Nov 12, 2026 evening (Nov 13 UTC; listed as WAS-DET)
- Kind: Altercation
- Reason: In a preseason Wizards-Pistons game on Oct. 10, 2026, Young and Jenkins shoved each other after contact near the sideline and both were ejected on second technical fouls.
- Source: EssentiallySports, Oct 10, 2026 (https://www.essentiallysports.com/nba-active-basketball-news-ref-ejects-trae-young-and-daniss-jenkins-while-heated-scuffle-adds-to-pistons-wizards-chaos/)
- Caveats: Single outlet, and preseason. The article labels Young as Washington's but does not explicitly state Jenkins's team (implied Detroit as the opponent). I could not find an ESPN/AP/NBA.com version. Suspensions: none mentioned. Check Jenkins's team on ESPN before approving.

```yaml
  - players: ["Trae Young", "Daniss Jenkins"]
    kind: Altercation
    date: "2026-10-10"
    reason: "In a Wizards-Pistons preseason game on Oct. 10, 2026, Young and Jenkins shoved each other after contact near the sideline and both were ejected after second technical fouls."
    sources:
      - {label: "EssentiallySports", url: "https://www.essentiallysports.com/nba-active-basketball-news-ref-ejects-trae-young-and-daniss-jenkins-while-heated-scuffle-adds-to-pistons-wizards-chaos/"}
```

## 3. Tyrese Haliburton vs. Jalen Brunson

- Game: Pacers @ Knicks, Nov 14, 2026 (listed as NYK-IND)
- Kind: Rivalry
- Reason: At a WWE event at Madison Square Garden in July 2026, Haliburton told Brunson "You can't beat me," a jab tied to the 2025 Eastern Conference Finals, and said he would see Brunson again in a couple of months.
- Source: Roundtable, Jul 20, 2026 (https://roundtable.io/sports/nba/pacers/news/tyrese-haliburton-puts-jalen-brunson-on-notice-during-wwe-appearance)
- Caveats: Verbal jab only, no on-court incident; single lesser-known outlet and I found no second source. I did not check Haliburton's availability for the game or his current roster status.

```yaml
  - players: ["Tyrese Haliburton", "Jalen Brunson"]
    kind: Rivalry
    date: "2026-07"
    reason: "At a WWE event at Madison Square Garden in July 2026, Haliburton told Brunson \"You can't beat me,\" a jab tied to the 2025 Eastern Conference Finals, and said he would see him again in a couple of months."
    sources:
      - {label: "Roundtable", url: "https://roundtable.io/sports/nba/pacers/news/tyrese-haliburton-puts-jalen-brunson-on-notice-during-wwe-appearance"}
```

## Not listed / could not verify

- NFL: no games fall inside the 2-day window (next NFL slate in the data is Nov 15-16), so NFL was not searched this run.
- Dropped for lack of two named players on the current matchup or an outdated roster: Westbrook/P.J. Washington vs. Clippers (2024 playoffs, Westbrook's current team unconfirmed), Isaiah Stewart's post-game jawing at Pelicans bench (Nov 2, 2026, no opposing player named), Jeremiah Fears/Luguentz Dort (Jan 2026, not in this window's games), Dillon Brooks/Egor Demin.
- Search leads seen but not fetched or confirmed: Ayo Dosunmu/Trae Young (Bulls-Hawks), Kris Dunn/Jabari Smith Jr. (Rockets-Jazz), Ausar Thompson/Anthony Davis (HITC page failed to load).
- Games with no qualifying, confirmed item found this run: CHA-PHX, MIN-DAL, PHI-TOR, CHI-ATL, CLE-MIA, HOU-UTA, MEM-NOP, OKC-LAC, ORL-MIL, SAC-POR, IND-NYK roster beyond the above. Searches were one standard query per game, so absence is not proof.
- Already in rivalries.yaml and not repeated: Nurkic/Marshall, Nurkic/P.J. Washington, Jaylin Williams/Champagnie, Mitchell/Champagnie, Wembanyama/Reid, Wembanyama/Holmgren, among others.
