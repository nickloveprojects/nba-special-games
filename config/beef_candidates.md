# Beef candidates (generated 2026-10-31) — for approval, NOT applied to rivalries.yaml / rivalries_nfl.yaml

Window: NBA 2026-10-31 and 2026-11-01; NFL 2026-11-01 and 2026-11-02. Pairs already in config were skipped (e.g. Holland II / Reid is already listed).
Every fact below was read from the linked article. Roster status of each player on game day was NOT independently re-checked except where noted.

## 1. Victor Wembanyama (SAS) vs Naz Reid (MIN) — Altercation
- Game: Timberwolves at Spurs, Oct. 31, 2026, 8:00 PM ET (Wembanyama and Reid's Game 4 incident: May 10, 2026)
- Reason: Wembanyama was ejected from Game 4 of the 2026 second-round series after elbowing Naz Reid (foul upgraded to Flagrant 2); the NBA did not suspend him.
- Sources: AP via WTOP (game recap, undated page, URL path 2026/05); Journal Gazette wire report (no suspension); Newsweek (Reid: "Pain is weakness leaving the body"). Date May 10 comes from the Yardbarker/EssentiallySports caption.
- Note: AP says the contact was to the neck, Newsweek and the wire report say face; the YAML avoids the body part. Reid's current-roster status not checked (Wembanyama confirmed SAS in today's data).

```yaml
  - players: ["Victor Wembanyama", "Naz Reid"]
    kind: Altercation
    reason: "Wembanyama was ejected from Game 4 of the 2026 Spurs-Timberwolves playoff series (May 10, 2026) after elbowing Reid and drawing a Flagrant 2; the NBA did not suspend him."
    sources:
      - {label: "AP via WTOP", url: "https://wtop.com/sports/2026/05/wembanyama-gets-ejected-early-in-spurs-wolves-game-4-for-elbowing-reid-and-drawing-a-flagrant-2-foul/"}
      - {label: "Journal Gazette", url: "https://www.journalgazette.net/sports/professional/nba/spurs-victor-wembanyama-wont-be-suspended-for-throwing-elbow/article_25d34d06-482a-5ce9-920c-077e5528e6dd.html"}
```

## 2. Rudy Gobert (MIN) vs Victor Wembanyama (SAS) — Backstory (lower confidence: one syndicated source)
- Game: Timberwolves at Spurs, Oct. 31, 2026, 8:00 PM ET (both confirmed on these teams in today's data)
- Reason: In Game 4 (May 10, 2026), Gobert's closeout on Wembanyama was ruled a Flagrant 1.
- Source: Yardbarker, syndicated from EssentiallySports (published May 12, 2026). The headline says "NBA Issues Warning" but the body does not describe a warning — not used. The article attributes to Gobert a remark that Wembanyama "asked me what kind of filter I had in my house"; context unclear, not used.

```yaml
  - players: ["Rudy Gobert", "Victor Wembanyama"]
    kind: Backstory
    reason: "Gobert's closeout on Wembanyama in Game 4 of the 2026 Timberwolves-Spurs playoff series (May 10, 2026) was upgraded to a Flagrant 1."
    sources:
      - {label: "Yardbarker (via EssentiallySports)", url: "https://www.yardbarker.com/nba/articles/rudy_goberts_dangerous_cheap_shot_at_victor_wembanyama_called_out_as_nba_issues_warning_to_timberwolves_star/s1_17730_43836768"}
```

## 3. Jahdae Barron (DEN) vs Travis Kelce (KC) — Backstory
- Game: Chiefs at Broncos, Nov. 1, 2026, 4:25 PM ET (incident: Denver's 22-19 win, mid-Nov. 2025; article Nov. 20, 2025)
- Reason: After beating KC, Barron reshared an Instagram post of him running into Kelce with the caption "Tell swift put me on a song RIGHT NOW," then took it down. SI's wording: he "appeared to throw shade."
- No Chiefs response reported. NEEDS CHECK: neither player appears in today's data and I did not confirm Kelce is on the Chiefs' active roster this season (he was reported as possibly retiring).

```yaml
  - players: ["Jahdae Barron", "Travis Kelce"]
    kind: Backstory
    reason: "After Denver's 22-19 win over Kansas City in November 2025, Barron reshared a post of him running into Kelce with the caption \"Tell swift put me on a song RIGHT NOW\" and later took it down."
    sources:
      - {label: "Sports Illustrated", url: "https://www.si.com/nfl/broncos-cb-shades-travis-kelce-taylor-swift-after-win-vs-chiefs-now-deleted-post"}
```

## Claims I could not verify (not proposed)
- A.J. Brown / Marshon Lattimore (Eagles at Commanders, Nov. 1): On3 describes Brown ripping off Lattimore's helmet in an "NFC Championship Game," but the page shows no date or season, and I did not confirm either player's current team. Not proposed.
- Eagles-Commanders Week 16 brawl (Dec. 20, 2025): PFN/On3 name ejections and fines (Steen, Kinlaw, Martin; Sainristil, Harris fined), but no two-player pair is documented, and PFN's score detail conflicts internally. Not proposed.
- Jonathon Cooper (DEN) profane posts about the Chiefs (Heavy/Fox, Dec. 28, 2025): directed at the team, no specific player named. Not proposed.
- No NBA candidates found for POR-UTA, PHI-CHA, ATL-NOP, SAC-MEM, CLE-MIL, OKC-HOU, BOS-ORL, BKN-IND, LAC-GSW, TOR-LAL, and no NFL candidates for the other games, within the searches done (searches were broad per slate, not exhaustive per team pair).
