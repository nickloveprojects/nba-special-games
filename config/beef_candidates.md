# Beef candidates (generated 2026-11-13)

Games checked: NBA Nov 13-14, 2026 (14 games) and NFL Nov 15-16, 2026 (web/data/nfl). Pairs already in rivalries.yaml / rivalries_nfl.yaml were skipped. Nothing here has been added to the config; approve and paste.

## 1. Victor Wembanyama vs. Draymond Green
- **Game:** Spurs at Warriors, Fri Nov 13, 2026, 9:30 PM ET
- **Kind:** Altercation
- **Reason (one sentence):** In the Nov. 14, 2025 NBA Cup game (Warriors 109-108), Green jawed with Wembanyama before an inbound play and Wembanyama answered with a dunk and then yelled at Green; Wembanyama said "you have to respond a certain way." No ejection, fine or suspension is reported.
- **Sources:**
  - CBS Sports, Nov. 15, 2025: https://www.cbssports.com/nba/news/victor-wembanyama-dunk-draymond-green-trash-talk
  - Dunkest, Nov. 15, 2025: https://www.dunkest.com/en/nba/news/224216/wemby-nearly-gets-into-a-fight-with-green-its-right-to-answer-provocations
- **Roster check:** Green re-signed with Warriors (NBC Sports, 2026-07-28: https://www.nbcsports.com/fantasy/basketball/player-news/2026-07-28/draymond-green-inks-one-year-deal-with-warriors). Not confirmed he is active/healthy for Nov. 13.
- Caveat: the CBS page was cut off in my fetch, so the dunk/yelling details and the quote rest partly on a summary of the rest of the page. Dunkest (read in full) confirms Green trying to rattle Wembanyama and the dunk in response; it also says Jeremy Sochan shoved Green, which I left out. Please open CBS before approving.

```yaml
  - players: ["Victor Wembanyama", "Draymond Green"]
    kind: Altercation
    date: "2025-11-14"
    reason: "In a Nov. 14, 2025 NBA Cup game, Green jawed with Wembanyama before an inbound play and Wembanyama answered with a dunk; Wembanyama said \"you have to respond a certain way.\""
    sources:
      - {label: "CBS Sports", url: "https://www.cbssports.com/nba/news/victor-wembanyama-dunk-draymond-green-trash-talk"}
      - {label: "Dunkest", url: "https://www.dunkest.com/en/nba/news/224216/wemby-nearly-gets-into-a-fight-with-green-its-right-to-answer-provocations"}
```

## Not verified / not listed
- Jalen Brunson vs. Tyrese Haliburton (Knicks-Pacers, Nov 13): Sportskeeda article is dated May 17, 2025 and describes playful trash talk at a WWE show; outside the 12-month window and not a real altercation. Excluded.
- Packers-Vikings (Nov 15): search surfaced older Jaire Alexander / Justin Jefferson / Aaron Jones items (2023-24). Not fetched and current rosters not confirmed. Excluded.
- Bills-Raiders spitting ejection (C.J. Gardner-Johnson, Oct 2026): Bills and Raiders are not playing each other on Nov 15. Excluded.
- Spurs/Wolves (Wembanyama-Naz Reid) and Thunder/Pelicans (Dort-Fears) items surfaced in searches involve teams not in this window's games, or are already listed. Excluded.
- Heat-Pistons, Clippers-Thunder, Chiefs-Falcons: searches found no two-player item I could confirm.
- Searches were run only for a subset of the matchups (Heat-Pistons, Knicks-Pacers, Spurs-Warriors, Clippers-Thunder, Packers-Vikings, a combined NFL query); the other games were not individually searched.
