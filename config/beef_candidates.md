# Beef candidates — run of 2026-10-30

Games covered: NBA Oct 30-31, NFL Nov 1-2. Nothing here has been added to config/rivalries*.yaml.

## 1. Jeremy Sochan vs. VJ Edgecombe — Knicks at 76ers, Fri Oct 30, 2026 (7:30 PM ET)

- **Kind:** Feud
- **Reason:** After the Knicks' 108-102 Game 2 win on May 6, 2026, Fox News reported Sochan was spotted talking trash to Edgecombe after the buzzer and had to be pulled away from the 76ers' bench, and that Edgecombe also had to be calmed down.
- **Source:** Fox News, Ryan Gaydos, May 7, 2026 — https://www.foxnews.com/sports/knicks-jeremy-sochan-76ers-vj-edgecombe-heated-exchange-new-yorks-game-2-win
- **Caveats:** The article says nothing came of it on the floor; no ejections, techs, or fines. The claim that Sochan "came over to troll" Edgecombe is attributed to a Clutch Points post on X (embed did not load), so it is left out of the reason. Sochan does not appear in the NBA data file for Oct 30, so confirm he is on the Knicks' active roster and plays.

```yaml
  - players: ["Jeremy Sochan", "VJ Edgecombe"]
    kind: Feud
    reason: "After the Knicks' Game 2 win in the May 2026 second-round series, Sochan was seen talking trash to Edgecombe after the buzzer and had to be pulled away from the 76ers' bench; Edgecombe also had to be calmed down."
    sources:
      - {label: "Fox News", url: "https://www.foxnews.com/sports/knicks-jeremy-sochan-76ers-vj-edgecombe-heated-exchange-new-yorks-game-2-win"}
```

## 2. Nikola Jokic vs. Devin Booker — Nuggets at Suns, Fri Oct 30, 2026

- **Kind:** Altercation
- **Reason:** Jokic was ejected for a Flagrant 2 on Cameron Payne in Game 4 of the 2021 Nuggets-Suns series, and Jokic and Booker then got into a heated confrontation.
- **Source:** Eurohoops, June 14, 2021 — https://www.eurohoops.net/en/nba-news/1217889/jokic-ejected-booker-payne/
- **Caveats:** The article gives no detail on the confrontation beyond "heated." It does not state the game date or round. Booker is in the Oct 30 data file; Jokic is not listed there, so confirm he plays. Older incident (2021), outside the 12-month window but a major one. Not a fight with a punishment.

```yaml
  - players: ["Nikola Jokic", "Devin Booker"]
    kind: Altercation
    reason: "Jokic was ejected for a Flagrant 2 on Cameron Payne in Game 4 of the 2021 Nuggets-Suns series, and he and Booker then got into a heated confrontation."
    sources:
      - {label: "Eurohoops", url: "https://www.eurohoops.net/en/nba-news/1217889/jokic-ejected-booker-payne/"}
```

## Claims not verified / rejected

- Eagles-Commanders brawl (Bleacher Report, Dec 20, 2025): ejected Tyler Steen, Javon Kinlaw, Quan Martin, but the article does not say which two players fought each other. Not a candidate.
- Heat's Bam Adebayo and Tyler Herro altercation (July 2026): Adebayo is not in this week's games vs. Herro's Bucks. Not fetched.
- Anthony Edwards / Kawhi Leonard (Wolves-Clippers): search snippets only, not fetched; not a confirmed two-player incident.
- Dillon Brooks vs. Donovan Mitchell, Brooks vs. Kevin Durant: Brooks is not on the relevant teams this week. Not fetched.
- No search was done for: ATL-NOP, POR-UTA, SAC-MEM, ORL-TOR, DET game, and most NFL games (LV-NYJ, MIN-DET, IND-JAX, NE game, CLE-PIT beyond the 2019 Garrett-Rudolph search, which was not fetched).
