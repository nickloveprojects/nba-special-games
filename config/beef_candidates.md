# Beef candidates — run of 2026-11-20

Games checked: NBA 2026-11-20 and 2026-11-21 (15 games); NFL 2026-11-22 (7 games). Nothing was added to config/rivalries.yaml or config/rivalries_nfl.yaml. Pairs already in rivalries.yaml were skipped.

**Roster caveat:** ESPN roster pages could not be fetched in this run, so neither player's current (Nov 2026) team is confirmed for the two items below; the articles only place them on those teams at the time. The app only shows a History box when both players are on the two teams in a game, so an entry for a player who has moved would simply not display. Please glance at both rosters before pasting.

## 1. Lu Dort (OKC) vs Jeremiah Fears (NOP)

- Game: Pelicans at Thunder, Fri 2026-11-20 (NBA).
- Kind: Altercation
- Reason: In the Thunder's 104-95 win on Jan. 27, 2026, Dort shoved Fears as time expired and both benches cleared; the NBA fined both players.
- Sources fetched: Sports Illustrated (Jan. 28, 2026), theScore (undated page, after Jan. 28, 2026; fines, no suspensions), Fox News (Jan. 30, 2026; Fears called Dort "soft" on social media, exact post not visible). Fine amount: theScore says $25,000 but does not say each or combined; the Fox10 headline from a search result (not fetched) says $25,000 each, so the YAML below avoids the amount.

```yaml
  - players: ["Luguentz Dort", "Jeremiah Fears"]
    kind: Altercation
    date: "2026-01-27"
    reason: "Dort shoved Fears as time expired in the Thunder's 104-95 win over the Pelicans on Jan. 27, 2026, and both benches cleared; the NBA fined both players and did not suspend either."
    sources:
      - {label: "Sports Illustrated", url: "https://www.si.com/nba/lu-dort-jeremiah-fears-get-into-postgame-altercation-after-thunder-win-over-pelicans"}
      - {label: "theScore", url: "https://thescore.com/nba/news/3466993"}
```

## 2. Bennedict Mathurin (IND) vs De'Andre Hunter (CLE)

- Game: Cavaliers at Pacers, Fri 2026-11-20 (NBA).
- Kind: Altercation
- Reason: In Game 4 of their 2025 playoff series, Mathurin hit Hunter in the chest with a closed fist and was ejected (flagrant 2); Hunter and Myles Turner got technicals.
- Sources fetched: NBA.com/AP (May 12, 2025), ESPN (May 12, 2025). Neither mentions fines or suspensions.

```yaml
  - players: ["Bennedict Mathurin", "De'Andre Hunter"]
    kind: Altercation
    date: "2025-05-12"
    reason: "Mathurin hit Hunter in the chest with a closed fist in Game 4 of the 2025 Cavaliers-Pacers playoff series and was ejected with a flagrant 2; Hunter was given a technical foul."
    sources:
      - {label: "NBA.com", url: "https://www.nba.com/news/pacers-bennedict-mathurin-ejected-game-4-hitting-deandre-hunter-cavaliers-2025-playoffs"}
      - {label: "ESPN", url: "https://africa.espn.com/nba/story/_/id/45103701/mathurin-ejected-hunter-turner-techs-cavs-pacers-altercation"}
```

## Claims not verified / left out

- Russell Westbrook vs Chris Boucher (Celtics at Kings, 11-21): NESN page has no publish date or byline date and does not name Westbrook's team; the two embraced afterward and Boucher's team is uncertain (trade speculation). Left out.
- Anthony Edwards vs Ja Morant (Grizzlies at Timberwolves, 11-21): Larry Brown Sports (Feb. 2, 2026) reports Edwards yelling "You can't do that, Ja!" at an injured Morant, with friendly words after the game; too mild and current teams unconfirmed. Left out.
- Dennis Schroder vs Luka Doncic (Lakers/Kings, 11-20): Dec. 28, 2025 tunnel incident and a 3-game suspension are documented (CBS Sports, Jan. 12, 2026), but today's data shows Schroder on Charlotte, so he is not in this game. Left out.
- Darius Slay vs Darnell Washington (Steelers at Eagles, 11-22): Dec. 2024 fight is documented (CBS, SI, PFT), but PFT reports Slay retired in March 2026. Left out.
- Eagles/Steelers Quinyon Mitchell vs Calvin Austin III (same Dec. 2024 scuffle): current rosters not verified. Left out.
- Searches for Nuggets-Rockets, Hornets-Hawks, Raptors-Pistons, Jazz-Suns, Nets-Magic, Bulls-Wizards, Bucks-76ers, Knicks-Blazers, Mavericks-Clippers, Pelicans-Spurs, Celtics-Kings and the other NFL games (Ravens-Panthers, Giants-Jaguars, Vikings-49ers, Cowboys-Titans, Cardinals-Chiefs) turned up no two-player item from a fetched, dated article that fit these games. Nuggets-Rockets only showed a coach ejection.
