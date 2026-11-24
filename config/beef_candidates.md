# Beef candidates (generated 2026-11-24, covers games 2026-11-24 to 2026-11-26)

Review only. Nothing here has been added to config/rivalries.yaml or config/rivalries_nfl.yaml.
Every reason states only what the fetched article says. Roster status of each player for the game date was NOT verified from a roster page unless noted.

## 1. Dillon Brooks vs. Kevin Durant
- Game: Suns at Rockets, Wed 2026-11-25, 8:30 PM ET (both are in web/data/2026-11-25.json entries: Durant HOU, Brooks PHX)
- Kind: Feud
- Reason: Houston Rockets On SI (Apr 9, 2026) says "the constant back-and-forth between Brooks and KD" got the most attention in an Apr 7, 2026 Rockets-Suns game, with Brooks "constantly after Durant early."
- Source: https://www.si.com/nba/rockets/onsi/news/watch-rockets-get-into-multiple-scuffles-with-suns-as-former-players-clash

```yaml
  - players: ["Kevin Durant", "Dillon Brooks"]
    kind: Feud
    date: "2026-04-07"
    reason: "In an April 7, 2026 Rockets-Suns game, Brooks and Durant had a constant back-and-forth, with Brooks \"constantly after Durant early,\" according to Rockets On SI."
    sources:
      - {label: "Rockets On SI", url: "https://www.si.com/nba/rockets/onsi/news/watch-rockets-get-into-multiple-scuffles-with-suns-as-former-players-clash"}
```

## 2. Jalen Green vs. Amen Thompson
- Game: Suns at Rockets, Wed 2026-11-25, 8:30 PM ET (Green PHX in entries)
- Kind: Altercation
- Reason: Same Rockets On SI article (Apr 9, 2026): the two former teammates "got physical and got into a tussle away from the play out-of-bounds" and Green grabbed Thompson's jersey later. The article also says it was "all mutual respect afterwards." No ejection or discipline is reported in the article.
- Source: same as above

```yaml
  - players: ["Jalen Green", "Amen Thompson"]
    kind: Altercation
    date: "2026-04-07"
    reason: "The former Rockets teammates got into a tussle away from the play in an April 7, 2026 Rockets-Suns game, according to Rockets On SI."
    sources:
      - {label: "Rockets On SI", url: "https://www.si.com/nba/rockets/onsi/news/watch-rockets-get-into-multiple-scuffles-with-suns-as-former-players-clash"}
```

## 3. Jalen Carter vs. Dak Prescott
- Game: Eagles at Cowboys, Thu 2026-11-26, 4:30 PM ET
- Kind: Altercation
- Reason: CBS Sports (Garrett Podell, Nov 21, 2025) says Carter was ejected in the Week 1 2025 opener after Prescott stepped between Carter and Cowboys guard Tyler Booker during an exchange of trash talk, and that "In response to Prescott's involvement, Carter spit on him."
- Source: https://www.cbssports.com/nfl/news/dak-prescott-cowboys-rematch-eagles-jalen-carter
- Note: Prescott confirmed on DAL in the data; Carter not in the entries list, roster not checked.

```yaml
  - players: ["Jalen Carter", "Dak Prescott"]
    kind: Altercation
    date: "2025-09-04"
    reason: "Carter was ejected in the 2025 season opener after he spit on Prescott during an exchange of trash talk, according to CBS Sports."
    sources:
      - {label: "CBS Sports", url: "https://www.cbssports.com/nfl/news/dak-prescott-cowboys-rematch-eagles-jalen-carter"}
```

## 4. Sydney Brown vs. Troy Pride
- Game: Eagles at Cowboys, Thu 2026-11-26
- Kind: Altercation
- Reason: Sports Illustrated (Liam McKeone, Dec 29, 2024): in the Eagles' 41-7 win, "Brown wound up slamming Cowboys cornerback Troy Pride to the ground as the fight spilled into the tunnel"; Brown was ejected for Philadelphia, and Pride and Jalen Brooks for Dallas.
- Source: https://www.si.com/nfl/cowboys-eagles-brawl-multiple-ejections-in-final-minutes-blowout
- Caveat: 2024 incident; neither player's current team/roster status checked. Use only if both are on the rosters.

```yaml
  - players: ["Sydney Brown", "Troy Pride"]
    kind: Altercation
    date: "2024-12-29"
    reason: "Brown slammed Pride to the ground as a fight spilled into the tunnel in the Eagles' 41-7 win over the Cowboys; both were ejected."
    sources:
      - {label: "Sports Illustrated", url: "https://www.si.com/nfl/cowboys-eagles-brawl-multiple-ejections-in-final-minutes-blowout"}
```

## 5. Jameson Williams vs. Tyrique Stevenson
- Game: Bears at Lions, Thu 2026-11-26, 1:00 PM ET (Williams DET in entries)
- Kind: Backstory
- Reason: Bears On SI (Dec 7, 2024): on Thanksgiving 2024, Williams drew a 15-yard penalty after going out of bounds and flipping the ball, striking Stevenson in the face; the league fined Stevenson $19,697 for unsportsmanlike conduct and did not fine Williams. SideLion Report (Dec 22, 2024) quotes both saying afterward there was no feud ("There's no bad blood," Stevenson).
- Sources: https://www.si.com/nfl/bears/onsi/tyrique-stevenson-draws-huge-fine-for-sideline-play-against-lions , https://sidelionreport.com/jameson-williams-and-tyrique-stevenson-both-dismiss-idea-of-a-feud-between-them
- Caveat: both players publicly dismissed a feud; Stevenson's current roster status not checked.

```yaml
  - players: ["Jameson Williams", "Tyrique Stevenson"]
    kind: Backstory
    date: "2024-11-28"
    reason: "On Thanksgiving 2024, Williams flipped the ball and struck Stevenson in the face after going out of bounds; Williams drew a 15-yard penalty and Stevenson was fined $19,697. Both later said there was no bad blood."
    sources:
      - {label: "Bears On SI", url: "https://www.si.com/nfl/bears/onsi/tyrique-stevenson-draws-huge-fine-for-sideline-play-against-lions"}
      - {label: "SideLion Report", url: "https://sidelionreport.com/jameson-williams-and-tyrique-stevenson-both-dismiss-idea-of-a-feud-between-them"}
```

## Claims NOT verified / not included
- Amon-Ra St. Brown vs. Equanimeous St. Brown (CBS Sports, Nov 22, 2023): body text partially truncated, quotes not verbatim-verified; Equanimeous's current team unchecked. Brothers, not clearly beef.
- Jalen Hurts vs. Trevon Diggs (SI, Sep 5, 2025): article itself says it "could have been good-natured ribbing"; not beef.
- Kevin Durant vs. Suns (NBA.com/AP Jan 2026, SI Mar 2026): aimed at the franchise/owner, no second named player.
- Pistons-Magic (Detroit at Orlando, Nov 24) and Pistons-Hornets fight: the one fetch (AOL) failed; search hits were mostly a Dec 2022 Killian Hayes/Moritz Wagner fight with both players' current status unknown. Nothing confirmed.
- Nuggets-Mavericks, Celtics-Wizards, Heat-76ers, Timberwolves-Thunder, Chiefs-Bills, Clippers-Grizzlies etc.: searches found no confirmed two-player item from a fetched article. Not fetched in full.
