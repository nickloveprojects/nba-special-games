# Beef candidates (run: 2026-11-14)

Games checked: NBA Nov 14-15 (14 games) and NFL Nov 15-16 (13 games). Nothing here has been added to the config files.

## 1. Jalen Ramsey vs Ja'Marr Chase (Steelers at Bengals, Sun 2026-11-15, 8:20 PM ET)

- Kind: Altercation
- Reason: Ramsey was ejected for throwing a punch at Chase in the Steelers-Bengals game on Nov 16, 2025; Ramsey said Chase spat on him, and Chase denied it.
- Source: CBS Sports (Bryan DeArdo), Nov 16, 2025: https://www.cbssports.com/nfl/news/bengals-steelers-fight-jalen-ramsey-ejected-jamarr-chase-aaron-rodgers
- Search results also showed pieces from Fox Sports, AOL, SI and TribLive that mention a suspension/fine for Chase. I did NOT fetch them, so the reason above leaves out any penalty.
- NOT VERIFIED: that Ramsey is still on the Steelers and Chase on the Bengals. ESPN roster pages could not be fetched. Check before pasting.
- NOT VERIFIED: the full CBS body. The fetch cut off partway through, so the ejection/spit details rest partly on a summary of the page. The headline and the date were read directly.

```yaml
  - players: ["Jalen Ramsey", "Ja'Marr Chase"]
    kind: Altercation
    date: "2025-11-16"
    reason: "Ramsey was ejected for throwing a punch at Chase in a Steelers-Bengals game on Nov. 16, 2025; Ramsey said Chase spat on him, and Chase denied it."
    sources:
      - {label: "CBS Sports", url: "https://www.cbssports.com/nfl/news/bengals-steelers-fight-jalen-ramsey-ejected-jamarr-chase-aaron-rodgers"}
```

## Not listed as candidates

All NBA pairs that turned up were already in config/rivalries.yaml, were not in these games, or were teammates. Pairs found and why they were left out:

- Jessie Bates III / Travis Kelce (Chiefs at Falcons): Fox News, Sep 20, 2024. Pre-game trash talk on a podcast, older than 12 months, not a fight. Roster status not verified.
- Khalil Mack / Derrick Henry (Chargers at Ravens): SI, Nov 28, 2024. Post-game comment and reply, older than 12 months. Roster status not verified.
- Trevon Diggs / Jauan Jennings (49ers at Cowboys): SI, Jul 30, 2023. Instagram exchange, old. Roster status not verified.
- Dion Dawkins / Micheal Clemons (Bills at Jets): ESPN and CBS Sports, Nov 2023 and Feb 2024. Tunnel spat, old. Roster status not verified. The ESPN page showed no date.

## Could not verify

- ESPN roster pages (all NFL teams above) were blocked, so current team membership is unconfirmed for every pair.
- Search results mentioned Jaylen Brown / Cooper Flagg (Mavericks at Celtics) as "beef rumors" that Brown cleared up. Not fetched, not listed.
- Tyler Herro / Bam Adebayo (Las Vegas exchange, reported by Fox News and Eurohoops): not fetched, and the teams do not meet in the games checked.
