# Beef candidates (run of 2026-11-11)

Games checked: NBA Nov 11 (WAS@IND, CLE@NYK, BOS@TOR, SAS@CHI, DEN@MEM, LAL@MIL, BKN@NOP, ORL@UTA, OKC@POR, GSW@HOU), NBA Nov 12 (TOR@PHI, DET@WAS, DAL@MIN, CHA@PHX), NFL Nov 12 (WSH@NYG).
Nothing here has been added to config/rivalries.yaml or config/rivalries_nfl.yaml. Approve by saying yes/no per item.

## Candidate 1: Jayden Daniels vs Brian Burns (NFL)

- Game: Washington Commanders at New York Giants, Thursday 2026-11-12, 8:15 PM ET
- Kind: Feud
- Reason: After the Sept. 7, 2025 season opener (Commanders 21-6), Burns said of Daniels "He talks a lot" and described him as talking in-game, and Daniels disputed Burns's account of what he said.
- Source: ESPN (John Keim), Sept. 9, 2025, "'He talks a lot': Jayden Daniels, Brian Burns sound off on in-game trash talk" - https://africa.espn.com/nfl/story/_/id/46209809/jayden-daniels-brian-burns-trash-talk-washington-commanders
- Caveats: the article is about trash talk, not a fight, so Feud is the strongest fit and "Altercation" would be wrong. The game date (Sept. 7) is inferred from "Sunday" in the article, so the YAML uses the month only. I could not confirm from the repo data that both players are still on those rosters for Nov. 12 (the NFL entries file for that date is empty); the app only shows the box if both are on the two teams.

```yaml
  - players: ["Jayden Daniels", "Brian Burns"]
    kind: Feud
    date: "2025-09"
    reason: "After the Sept. 2025 Commanders-Giants opener, Burns said Daniels \"talks a lot\" in games and Daniels disputed Burns's account of what he said."
    sources:
      - {label: "ESPN", url: "https://africa.espn.com/nfl/story/_/id/46209809/jayden-daniels-brian-burns-trash-talk-washington-commanders"}
```

## Claims I could not verify (not listed as candidates)

- Marshon Lattimore suplexing Wan'Dale Robinson in a Giants-Commanders game (On3, "Fight breaks out between Giants, Commanders after Marshon Lattimore suplex"): the page shows no byline or publication date, and does not state which team either player is on or the calendar date of the game. Needs a dated source (e.g. ESPN or NFL.com) and a roster check before it can be added.
- Search results only surfaced older or non-matchup items for CLE@NYK, BOS@TOR, SAS@CHI, DEN@MEM, LAL@MIL and other games, and I did not fetch or confirm any article naming two specific players for them. The Mitchell Robinson / Dyson Daniels and Pistons-Hornets items found are already in rivalries.yaml, and the Dillon Brooks / John Collins preseason scuffle (Eurohoops, Oct. 6, 2026) involves players whose teams (PHX, DET) do not play each other in this window.
- Coverage is limited: one standard search per few games, not per game, so absence of candidates is not proof of no beef.
