# Beef candidates — run of 2026-11-16

Games checked: NBA 11/16 (ORL@BOS, CHI@CLE, MEM@WAS, PHI@BKN, HOU@MIA, POR@MIN, GSW@NOP, DEN@PHX), NBA 11/17 (NYK@TOR, DET@SAS, UTA@LAC, CHA@LAL, POR@MIN), NFL LAC@BAL (11/16, 8:15 PM ET).
Every candidate below was confirmed by fetching the article. Nothing was added to rivalries.yaml or rivalries_nfl.yaml.

**Roster caveat:** I confirmed the incident from the articles, but did not confirm that each player is on the same team now and active for tonight's game. web/data only lists a subset of players per team (Keldon Johnson is listed for SAS tonight; Brooks, Murray, Durant, Herro, Duren, Cunningham are not in the entries). Please check availability before pasting.

---

## 1. Dillon Brooks (Suns) vs. Jamal Murray (Nuggets)

- Game: Nuggets @ Suns, Mon 2026-11-16, 9:00 PM ET
- Kind: Altercation
- Reason (checkable): Brooks was ejected after kicking Murray in the groin in the Suns-Nuggets game on Oct. 30, 2026; officials upgraded the foul to a Flagrant 2.
- Also in the articles: Murray said afterward he didn't think the kick was intentional, called Brooks a buddy, and said Brooks "might have flopped a little bit." No league suspension or fine was reported in either article.
- Sources:
  - Associated Press via Arizona's Family (KPHO), published Oct. 30, 2026: https://www.azfamily.com/2026/10/31/dillon-brooks-ejected-game-kicking-nuggets-murray-groin/
  - Associated Press (David Brandt) via WJXT News4JAX, published Oct. 30, 2026: https://www.news4jax.com/sports/2026/10/31/suns-dillon-brooks-ejected-from-game-for-kicking-nuggets-jamal-murray-in-the-groin/
- Note: Brooks is already in rivalries.yaml with LeBron James and is not paired with Murray there.

```yaml
  - players: ["Dillon Brooks", "Jamal Murray"]
    kind: Altercation
    date: "2026-10-30"
    reason: "Brooks was ejected after kicking Murray in the groin in a Suns-Nuggets game on Oct. 30, 2026; officials upgraded the foul to a Flagrant 2."
    sources:
      - {label: "AP via Arizona's Family", url: "https://www.azfamily.com/2026/10/31/dillon-brooks-ejected-game-kicking-nuggets-jamal-murray-in-the-groin/"}
      - {label: "AP via News4JAX", url: "https://www.news4jax.com/sports/2026/10/31/suns-dillon-brooks-ejected-from-game-for-kicking-nuggets-jamal-murray-in-the-groin/"}
```

---

## 2. Keldon Johnson (Spurs) vs. Jalen Duren (Pistons)

- Game: Pistons @ Spurs, Tue 2026-11-17, 8:00 PM ET
- Kind: Altercation
- Reason (checkable): Johnson and Duren were each called for a technical foul after Johnson pushed Cade Cunningham and Duren pointed his finger in Johnson's face in the Spurs-Pistons game on Feb. 23, 2026.
- Sources:
  - Associated Press (Larry Lage) via WDIV ClickOnDetroit, published Feb. 23, 2026: https://www.clickondetroit.com/sports/2026/02/24/tempers-flare-in-spurs-pistons-game-in-a-matchup-of-2-of-nbas-top-teams/
  - Larry Brown Sports (Darryn Albert), published Feb. 23, 2026: https://larrybrownsports.com/basketball/jalen-duren-keldon-johnson-incident/742687
- Note: the AP story says Cunningham was called for an offensive foul for knocking Stephon Castle down, which came before Johnson's push. Neither article reports a fine or suspension for this incident. Duren is already in the file with Moussa Diabate and Miles Bridges, but not with Johnson.

```yaml
  - players: ["Keldon Johnson", "Jalen Duren"]
    kind: Altercation
    date: "2026-02-23"
    reason: "Johnson pushed Cade Cunningham and Duren pointed a finger in Johnson's face in a Spurs-Pistons game on Feb. 23, 2026; Johnson and Duren were each called for a technical foul."
    sources:
      - {label: "AP via WDIV", url: "https://www.clickondetroit.com/sports/2026/02/24/tempers-flare-in-spurs-pistons-game-in-a-matchup-of-2-of-nbas-top-teams/"}
      - {label: "Larry Brown Sports", url: "https://larrybrownsports.com/basketball/jalen-duren-keldon-johnson-incident/742687"}
```

### 2b. Keldon Johnson (Spurs) vs. Cade Cunningham (Pistons) — same game, same sources

- Kind: Altercation
- Reason (checkable): After Cunningham was called for an offensive foul for knocking Stephon Castle down, Johnson responded by pushing Cunningham (AP wording; Larry Brown Sports calls it a "light shove").

```yaml
  - players: ["Keldon Johnson", "Cade Cunningham"]
    kind: Altercation
    date: "2026-02-23"
    reason: "In a Spurs-Pistons game on Feb. 23, 2026, Cunningham was called for an offensive foul for knocking Stephon Castle down, and Johnson responded by pushing Cunningham."
    sources:
      - {label: "AP via WDIV", url: "https://www.clickondetroit.com/sports/2026/02/24/tempers-flare-in-spurs-pistons-game-in-a-matchup-of-2-of-nbas-top-teams/"}
      - {label: "Larry Brown Sports", url: "https://larrybrownsports.com/basketball/jalen-duren-keldon-johnson-incident/742687"}
```

---

## 3. Kevin Durant (Rockets) vs. Tyler Herro (Heat)

- Game: Rockets @ Heat, Mon 2026-11-16, 7:30 PM ET
- Kind: Feud (verbal altercation)
- Reason (checkable): Durant and Herro were jawing through much of the first quarter of a Rockets-Heat game on Feb. 28, 2026, and both were assessed technical fouls; Herro said afterward that Durant was saying he couldn't guard and he said something back.
- Source (single outlet, lower-tier): EssentiallySports (Pranav Kotai), published Mar. 1, 2026: https://www.essentiallysports.com/nba-active-basketball-news-did-tyler-herro-troll-kevin-durant-over-alleged-burners-fact-checking-truth-behind-heated-altercation/
- Both players downplayed it: Herro said "Nothing crazy" and Durant said "I got respect for Tyler."
- The Feb. 28 date comes from an embedded post on that page; the article body says only "Saturday." Consider "2026-02" if you want a looser date.

```yaml
  - players: ["Kevin Durant", "Tyler Herro"]
    kind: Feud
    date: "2026-02-28"
    reason: "Durant and Herro jawed at each other in the first quarter of a Rockets-Heat game on Feb. 28, 2026, and both were assessed technical fouls."
    sources:
      - {label: "EssentiallySports", url: "https://www.essentiallysports.com/nba-active-basketball-news-did-tyler-herro-troll-kevin-durant-over-alleged-burners-fact-checking-truth-behind-heated-altercation/"}
```

---

## Claims I could not verify (not listed above)

- A viral clip claims Herro said "I know what burners you run" to Durant. EssentiallySports says no mic picked up what Herro said and the claim is unconfirmed, so it is left out of the reason text.
- Austin Reaves (Lakers) ejection vs. Hornets (Sportskeeda): the article says the two technicals were for complaining to the referee, not for contact with a Hornets player. No player pair. Dropped.
- Timberwolves-Trail Blazers, Feb. 24, 2026 (AP via OPB): described as "physical," but no ejection, scuffle or trash talk between named players. Dropped.
- Warriors-Pelicans, Cavaliers-Bulls, Grizzlies-Wizards, 76ers-Nets, Knicks-Raptors, Celtics-Magic, Clippers-Jazz: searches returned only older or unrelated items (game recaps, teammate disputes, 2023-2025 incidents already covered or outside the window). Nothing fetched and confirmed for a named pair.
- Chargers-Ravens (NFL): search results were about the 2024 Harbaugh Bowl and a Khalil Mack/Derrick Henry exchange; I did not fetch those articles, so nothing is listed. Khalil Mack's current team is unconfirmed.
