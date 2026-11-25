# Beef candidates (run: 2026-11-25)

Scope: NBA games 2026-11-25 and 2026-11-27, NFL games 2026-11-25 to 2026-11-27. Nothing here has been added to config/rivalries*.yaml. Approve a pair and paste its YAML block.

Verification note: article text was read by a fetch subagent, not by me directly. Only what the article states is used below.

## 1. Jalen Green (PHX) vs Amen Thompson (HOU)

- Game: Suns at Rockets, 2026-11-25, 8:30 PM ET (Toyota Center)
- Kind: Altercation
- Reason: In a Rockets-Suns game in Phoenix in April 2026 (Rockets won 119-105), after Thompson's layup was blocked by Green, the two former teammates "got physical and got into a tussle" away from the play. No ejections, technicals or fines are mentioned.
- Source: Maanav Gupta, Rockets On SI (SI.com), published 2026-04-09: https://www.si.com/nba/rockets/onsi/news/watch-rockets-get-into-multiple-scuffles-with-suns-as-former-players-clash
- Caveats: The article gives the day as "Tuesday night" with a photo caption of Apr 7, 2026; the exact date is inferred, so the YAML uses 2026-04. The Thompson quote ("I'm on you boy!") comes via an embedded post, so it is left out of the reason. Single outlet.

```yaml
  - players: ["Jalen Green", "Amen Thompson"]
    kind: Altercation
    date: "2026-04"
    reason: "In a Rockets-Suns game in Phoenix in April 2026, the former teammates got into a tussle away from the play after Thompson's layup was blocked by Green."
    sources:
      - {label: "Rockets On SI", url: "https://www.si.com/nba/rockets/onsi/news/watch-rockets-get-into-multiple-scuffles-with-suns-as-former-players-clash"}
```

## 2. Kevin Durant (HOU) vs Dillon Brooks (PHX)  (weaker, your call)

- Game: Suns at Rockets, 2026-11-25, 8:30 PM ET
- Kind: Feud
- Reason: Same April 2026 Rockets-Suns game: the article says Brooks was "constantly after Durant early," and Durant afterward said Brooks "is not that much of a concern to me."
- Source: Rockets On SI, 2026-04-09 (same link as above)
- Caveats: The widely shared "My worst season is better than your best" line is attributed only to social-media lip readers ("supposedly"), so it is NOT used. Mild chippiness rather than a fight; no penalties mentioned. The Durant quote is relayed by the fetch subagent in part; re-read before approving.

```yaml
  - players: ["Kevin Durant", "Dillon Brooks"]
    kind: Feud
    date: "2026-04"
    reason: "In an April 2026 Rockets-Suns game, Brooks was \"constantly after Durant early\" per Rockets On SI; afterward Durant said Brooks \"is not that much of a concern to me.\""
    sources:
      - {label: "Rockets On SI", url: "https://www.si.com/nba/rockets/onsi/news/watch-rockets-get-into-multiple-scuffles-with-suns-as-former-players-clash"}
```

## Not listed / could not verify

- Trey Smith (KC) vs Dorian Williams (BUF), Chiefs-Bills 2026-11-26: FanSided (2024-11-17) describes a skirmish with offsetting unnecessary-roughness penalties (Smith and Epenesa), no ejections. It is older than 12 months and minor, and neither is a QB/RB/WR/TE/K so no card would show. Not listed.
- D'Andre Swift (CHI) vs Lions, 2026-11-26: the only article found (FOX 32, 2024) quotes Swift saying "It's just another team"; no named Lions player. No beef.
- Durant/Ishbia social-media spat: involves the Suns owner, not two players. Excluded.
- Coby White (CHA) vs Bulls: SI headlines suggest he "took the high road"; no player-vs-player beef found.
- Search snippets only, not fetched or confirmed: Timberwolves-Thunder (a Finch ejection, not a player feud), Knicks-Cavaliers (no relevant result).
- Not searched this run: MIA@PHI (LeBron vs Heat), the 2026-11-27 NBA slate, and the NFL games GB@LAR, PHI@DAL, DEN@PIT.
