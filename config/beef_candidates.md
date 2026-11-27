# Beef candidates (run: 2026-11-27)

Window checked: NBA 2026-11-27 and 11-28; NFL 2026-11-27 through 11-29.
Nothing here has been added to config/rivalries.yaml or config/rivalries_nfl.yaml. Reply yes or no per item.

## NBA
No new candidates. Searches surfaced Marcus Smart / Charles Bassey (Eurohoops, 2026-11-12) but Bassey's team is not stated in the article and the pair is not scheduled to meet in this window (Rockets host the 76ers on 11-28). Other hits (Draymond Green / Dillon Brooks, Ja Morant / Klay Thompson) involve players on teams not playing each other in the window.

## NFL

### 1. Mike Evans vs. Trevon Diggs
- Game: Seahawks at 49ers, Sun 2026-11-29, 1 PM ET (Evans is a 49ers WR; Diggs a Seahawks CB per the articles)
- Kind: Feud
- Reason: In the 49ers' 32-29 win over Seattle on Oct. 11, 2026, Diggs talked trash to Evans, who grabbed Diggs' jersey and turned him around to read his name; Diggs swatted Evans' hand away.
- Sources: Newsweek, Oct. 11, 2026 (fetched, confirms the above); CBS Sports, Oct. 11, 2026 (fetched, headline/subhead confirms the "Who are you?" exchange).
- Unverified: both are still on those rosters as of today (not confirmed); the CBS body was only partly readable, and its description of who pushed first differs from Newsweek, so the reason uses Newsweek's wording only.

```yaml
  - players: ["Mike Evans", "Trevon Diggs"]
    kind: Feud
    date: "2026-10-11"
    reason: "In the 49ers' 32-29 win over Seattle on Oct. 11, 2026, Diggs talked trash to Evans, who grabbed Diggs' jersey and turned him around to read his name; Diggs swatted Evans' hand away."
    sources:
      - {label: "Newsweek", url: "https://www.newsweek.com/sports/nfl/49ers-mike-evans-hilariously-burned-seahawks-trevon-diggs-who-are-you-12553596"}
      - {label: "CBS Sports", url: "https://www.cbssports.com/nfl/news/49ers-seahawks-mike-evans-trolls-trevon-diggs"}
```

### 2. Julius Chestnut vs. Logan Cooke
- Game: Titans at Jaguars, Sun 2026-11-29, 1 PM ET (Chestnut a Titans RB, Cooke a Jaguars punter per the 2025 articles)
- Kind: Altercation
- Reason: In the Jaguars' 25-3 win over the Titans on Nov. 30, 2025, Cooke and Chestnut were involved in a scuffle, and Chestnut said after the game that Cooke "said he was going to kill me."
- Source: Fox News (Ryan Gaydos), Dec. 1, 2025 (fetched). The article's own text calls Cooke's alleged remark "vile"; the "kill me" claim is Chestnut's account only.
- Unverified: whether both are still on these rosters (a year-old story; not confirmed); part of the fetched article came back summarized rather than verbatim.
- Note: neither player is in a card position that this repo shows for a punter, but Chestnut is an RB so the card can appear.

```yaml
  - players: ["Julius Chestnut", "Logan Cooke"]
    kind: Altercation
    date: "2025-11-30"
    reason: "In the Jaguars' 25-3 win over the Titans on Nov. 30, 2025, the two were involved in a scuffle, and Chestnut said afterward that Cooke told him he was going to kill him."
    sources:
      - {label: "Fox News", url: "https://www.foxnews.com/sports/jaguars-pro-bowl-punter-accused-threatening-titans-player-during-game"}
```

### 3. Arden Key vs. Anton Harrison
- Game: Titans at Jaguars, Sun 2026-11-29
- Kind: Altercation
- Reason: On Nov. 30, 2025, Harrison took exception to Key's hit on Trevor Lawrence and the two locked horns; Key was penalized for roughing the passer and a personal foul.
- Source: Fox News (Ryan Gaydos), Nov. 30, 2025 (fetched).
- Unverified: current rosters; the repo only shows cards for QB/RB/WR/TE/K, so neither (DE, OT) would display a card. Probably not worth adding.

```yaml
  - players: ["Arden Key", "Anton Harrison"]
    kind: Altercation
    date: "2025-11-30"
    reason: "On Nov. 30, 2025, Harrison took exception to Key's hit on Trevor Lawrence and the two locked horns; Key was penalized for roughing the passer and a personal foul."
    sources:
      - {label: "Fox News", url: "https://www.foxnews.com/sports/titans-jaguars-players-fight-after-big-hit-trevor-lawrence"}
```

## Claims not verified
- Current-roster status of every player above (the data files list only featured players).
- Marcus Smart / Charles Bassey team details (Bassey's team not stated in the article).
- No other game in the window produced an article-confirmed two-player item.
