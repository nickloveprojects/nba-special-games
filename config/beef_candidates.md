# Beef candidates — run of 2026-11-17

Games checked: NBA 2026-11-17 (5 games) and 2026-11-18 (12 games); NFL 2026-11-19 (IND at HOU).
Nothing here has been added to config/rivalries.yaml or config/rivalries_nfl.yaml. Approve a candidate and its YAML block can be pasted in.

Coverage note: I confirmed articles for the items below. Searches for several other games (TOR-NYK, CHA-LAL, GSW-DAL, DEN-BOS, ATL-OKC, MEM-CLE, IND-HOU and others) returned nothing that named two players on those rosters with a dated, confirmed article. Not every game got its own search.

## 1. Keldon Johnson vs Jalen Duren — SAS at DET, 2026-11-17 (tonight)
- Kind: Altercation
- Reason: In a Spurs-Pistons game on Feb. 23, 2026, Duren pointed his finger in Johnson's face, and after a review both were called for technical fouls (per AP).
- Sources: ESPN (AP), Feb. 24, 2026; WTOP (AP), Feb. 2026.
- Note: neither article reports an ejection.

```yaml
  - players: ["Keldon Johnson", "Jalen Duren"]
    kind: Altercation
    date: "2026-02-23"
    reason: "In a Spurs-Pistons game on Feb. 23, 2026, Duren pointed his finger in Johnson's face and both were called for technical fouls after a review."
    sources:
      - {label: "ESPN (AP)", url: "https://africa.espn.com/nba/story/_/id/48019084/spurs-humble-pistons-potential-nba-finals-preview"}
      - {label: "WTOP (AP)", url: "https://wtop.com/sports/2026/02/tempers-flare-in-1st-half-of-spurs-pistons-game-in-a-matchup-of-2-of-nbas-top-teams/"}
```

## 2. Keldon Johnson vs Cade Cunningham — SAS at DET, 2026-11-17 (tonight)
- Kind: Altercation
- Reason: In the same Feb. 23, 2026 game, Cunningham was called for an offensive foul for knocking Stephon Castle down, and Johnson responded by pushing Cunningham (per AP).
- Sources: same two AP stories as above.
- Note: confirm Cunningham is on tonight's Pistons roster/active before pasting.

```yaml
  - players: ["Keldon Johnson", "Cade Cunningham"]
    kind: Altercation
    date: "2026-02-23"
    reason: "In a Spurs-Pistons game on Feb. 23, 2026, Johnson pushed Cunningham after Cunningham was called for an offensive foul for knocking Stephon Castle down."
    sources:
      - {label: "ESPN (AP)", url: "https://africa.espn.com/nba/story/_/id/48019084/spurs-humble-pistons-potential-nba-finals-preview"}
      - {label: "WTOP (AP)", url: "https://wtop.com/sports/2026/02/tempers-flare-in-1st-half-of-spurs-pistons-game-in-a-matchup-of-2-of-nbas-top-teams/"}
```

## 3. Tyler Herro vs Bam Adebayo — MIL at MIA, 2026-11-18
- Kind: Backstory (former teammates; Herro now with the Bucks after the offseason trade)
- Reason: On July 10, 2026, Adebayo reportedly struck Herro at a Las Vegas Summer League practice facility over critical comments Herro reportedly made about him; the Heat said they were aware of an incident and declined comment.
- CAUTION: both articles rely on anonymous sources (AP: "a person with knowledge of the matter"; SI relays ESPN's Shams Charania). Neither player nor team confirmed details. The two articles also differ on whether the comments were Instagram posts or direct messages. Recommend approving only if "reportedly" wording is acceptable. The reason below is worded as a report.
- Also confirm Adebayo is active for the game.
- Sources: FOX Sports (AP), updated Jul. 11, 2026; Milwaukee Bucks On SI, Jul. 11, 2026.

```yaml
  - players: ["Tyler Herro", "Bam Adebayo"]
    kind: Backstory
    date: "2026-07-10"
    reason: "Former Heat teammates; on July 10, 2026, Adebayo reportedly struck Herro during an altercation in Las Vegas over critical comments Herro had reportedly made about him (AP, citing an anonymous source). Herro has since been traded to the Bucks."
    sources:
      - {label: "FOX Sports (AP)", url: "https://www.foxsports.com/articles/nba/former-heat-teammates-bam-adebayo-tyler-herro-have-brief-altercation-in-las-vegas-ap-source-says"}
      - {label: "Milwaukee Bucks On SI", url: "https://www.si.com/nba/bucks/onsi/how-tyler-herro-bucks-responded-to-the-altercation-with-bam-adebayo-01kx8s1zh486"}
```

## Claims I could not verify (not listed above)
- Donovan Mitchell / Desmond Bane loose-ball scrum, Cavaliers vs Grizzlies (MEM at CLE, 11-18): the On3 page gives no publication or game date, only "Sunday night," and says no punches appeared to be thrown. Not usable without a dated source.
- Colts-Texans (IND at HOU, 11-19): search results were only older (2019-2025) trash talk and general rivalry pieces; none fetched or confirmed for two named players on today's rosters.
- Knicks-Hawks Mitchell Robinson / Dyson Daniels fight (April 2026): already in rivalries.yaml, and neither team plays in the window.
