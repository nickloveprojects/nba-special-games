# Beef candidates (run of 2026-11-26)

Window checked: NBA games 2026-11-27 and 2026-11-28 (16 games); NFL games 2026-11-26 and 2026-11-27 (4 games; no NFL games on 11-28).
Nothing here has been added to config/rivalries.yaml or config/rivalries_nfl.yaml. Approve or reject each one.

**Roster caveat for every item below:** the article confirms the incident, but I could not confirm from the repo data or a fetched page that both players are on those teams for the game. The data files only list featured players. Check the ESPN rosters before pasting a block.

---

## 1. Jarred Vanderbilt (Lakers) vs Jeremy Sochan (Spurs)
- Game: Lakers at Spurs, 2026-11-27, 9:30 PM ET (NBA)
- Kind: Altercation
- Reason: Both were ejected for fighting technicals after a shoving exchange in a March 2025 Lakers-Spurs game (SI), and in January 2026 Vanderbilt poked Sochan in the face after a Spurs win while teammates stepped in (ESPN).
- Sources: ESPN, Michael C. Wright, Jan 8, 2026; Sports Illustrated, Stephen Douglas, Mar 18, 2025
  - https://africa.espn.com/nba/story/_/id/47547923/spurs-sochan-downplays-confrontation-lakers-vanderbilt
  - https://www.si.com/nba/jarred-vanderbilt-jeremy-sochan-ejected-fighting-lakers-spurs
- Notes: ESPN says no ejections, fines or suspensions for the January incident and gives no calendar date ("Wednesday"). SI gives no calendar date either ("Monday"). Both dates in the YAML are month-level.
- Roster check needed: Vanderbilt on the Lakers and Sochan on the Spurs for 2026-27.

```yaml
  - players: ["Jarred Vanderbilt", "Jeremy Sochan"]
    kind: Altercation
    date: "2026-01"
    reason: "Both were ejected for fighting technicals after a shoving exchange in a March 2025 Lakers-Spurs game, and in January 2026 Vanderbilt poked Sochan in the face after a Spurs win while teammates stepped in."
    sources:
      - {label: "ESPN", url: "https://africa.espn.com/nba/story/_/id/47547923/spurs-sochan-downplays-confrontation-lakers-vanderbilt"}
      - {label: "Sports Illustrated", url: "https://www.si.com/nba/jarred-vanderbilt-jeremy-sochan-ejected-fighting-lakers-spurs"}
```

## 2. Tyrique Stevenson (Bears) vs Jameson Williams (Lions)
- Game: Bears at Lions, 2026-11-26, 1:00 PM ET (NFL, today)
- Kind: Altercation
- Reason: On Thanksgiving 2024 Stevenson tripped Williams on the sideline, Williams threw the ball at Stevenson and drew a taunting penalty, and Stevenson was fined nearly $20,000. The article says both denied any bad blood afterward.
- Source: SideLion Report, Brad Berreman, Dec 22, 2024
  - https://sidelionreport.com/jameson-williams-and-tyrique-stevenson-both-dismiss-idea-of-a-feud-between-them
- Notes: The fine amount is the article's wording ("nearly $20,000"); it links to a separate article I did not fetch. Both players called it "no bad blood" in the same article, so "Altercation" fits better than "Feud". Single source, Lions fan site.
- Roster check needed: Stevenson on the Bears and Williams on the Lions for 2026.

```yaml
  - players: ["Jameson Williams", "Tyrique Stevenson"]
    kind: Altercation
    date: "2024-11"
    reason: "On Thanksgiving 2024 Stevenson tripped Williams on the sideline, Williams threw the ball at Stevenson and drew a taunting penalty, and Stevenson was fined nearly $20,000; both later said there was no bad blood."
    sources:
      - {label: "SideLion Report", url: "https://sidelionreport.com/jameson-williams-and-tyrique-stevenson-both-dismiss-idea-of-a-feud-between-them"}
```

## 3. Jalen Carter (Eagles) vs Dak Prescott (Cowboys)
- Game: Eagles at Cowboys, 2026-11-26, 4:30 PM ET (NFL, today)
- Kind: Altercation
- Reason: Carter was ejected in Week 1 of the 2025 season for spitting on Prescott.
- Source: CBS Sports, Garrett Podell, Nov 21, 2025
  - https://www.cbssports.com/nfl/news/dak-prescott-cowboys-rematch-eagles-jalen-carter
- Notes: The fetch of the article body was truncated; the ejection-for-spitting claim is in the verbatim headline/subhead and meta description. Prescott is confirmed on DAL in the repo data. Carter's 2026 roster status is not confirmed. No fine or suspension is stated.

```yaml
  - players: ["Jalen Carter", "Dak Prescott"]
    kind: Altercation
    date: "2025-09"
    reason: "Carter was ejected in Week 1 of the 2025 season for spitting on Prescott."
    sources:
      - {label: "CBS Sports", url: "https://www.cbssports.com/nfl/news/dak-prescott-cowboys-rematch-eagles-jalen-carter"}
```

## 4. Travis Kelce (Chiefs) vs Jordan Phillips (Bills)  -- weakest, probably skip
- Game: Chiefs at Bills, 2026-11-26, 8:20 PM ET (NFL, today)
- Kind: Altercation
- Reason: After the AFC Championship Game, Phillips was fined $6,722 for hitting Kelce in the head with his helmet, and Kelce was fined $11,255 for taunting Damar Hamlin.
- Source: Bolavip US, Miguel Angel Fernandez Castro, Feb 2, 2025
  - https://bolavip.com/en/nfl/nfl-imposes-strong-fine-on-josh-allen-teammate-for-incident-with-travis-kelce-after-bills-loss-to-chiefs-in-playoffs
- Notes: Lower-tier outlet, single source, no calendar date for the game in the article. I could not confirm Phillips is still on the Bills; if he is not, this does not apply. Do not approve unless the roster check passes.

```yaml
  - players: ["Travis Kelce", "Jordan Phillips"]
    kind: Altercation
    date: "2025-01"
    reason: "After the 2025 AFC Championship Game, Phillips was fined $6,722 for hitting Kelce in the head with his helmet, and Kelce was fined $11,255 for taunting Damar Hamlin."
    sources:
      - {label: "Bolavip US", url: "https://bolavip.com/en/nfl/nfl-imposes-strong-fine-on-josh-allen-teammate-for-incident-with-travis-kelce-after-bills-loss-to-chiefs-in-playoffs"}
```

---

## Claims I could not verify (not listed above)
- Trey Smith (Chiefs) vs Dorian Williams (Bills): FanSided (Nov 17, 2024) describes a mini-brawl with offsetting unnecessary-roughness penalties and no ejections or fines. Too minor and roster status unconfirmed, so left out.
- Hawks-Celtics (11-27): search results show a Tatum/Brown "heated tussle" with Hawks players and a Marcus Smart/Trae Young fight (Smart is no longer on either team as far as I could tell). I did not fetch these, so no pair is listed. Boston.com (Nov 12, 2026) covers a Tatum-Brown pregame interaction, but that is a Celtics-76ers game, not this one.
- 76ers-Rockets (11-28): a B/R item about Joel Embiid trolling Alperen Sengun on Instagram after a 76ers win. Not fetched and the item is a social media jab; not verified.
- Thunder-Bucks (11-28): an SI piece on an OKC big man's dust-up with Bucks' Andre Jackson (December 2024). Not fetched; Jackson's current team unconfirmed.
- Magic-Wizards, Nets-Raptors, Nets-Hornets, Pacers-Bulls, Nuggets-Jazz, Pelicans-Clippers, Mavericks-Suns, Warriors-Blazers, Grizzlies-Wolves, Heat-Knicks, Pistons-Bucks, Pacers-76ers: searches surfaced only incidents that involve other teams, pairs already in rivalries.yaml (Nurkic/Marshall, Nurkic/Washington, Dyson Daniels/Mitchell Robinson, Jokic/McDaniels, Champagnie/Mitchell, Suggs/Drummond, Bridges/Duren, Stewart/Bridges), or teammates (Maxey/Edgecombe). Nothing new that I confirmed.
- NFL Broncos-Steelers (11-27): only results about Josh Allen/Cam Heyward and Ramsey/Chase, neither involving this game. Nothing found.
