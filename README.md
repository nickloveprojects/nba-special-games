# Backstory Sports

A daily tracker that flags players in the day's NBA games (or the next slate) who have a **Revenge**, **Hometown**, or **Birthday** angle. Each flag carries a confidence level and source links.

## Where the data comes from

| Need | Source |
|---|---|
| Schedule, tip times, arenas | ESPN public scoreboard JSON |
| Rosters, birthdates, birthplaces | ESPN team roster JSON |
| Career team history, season averages | ESPN athlete stats JSON |
| Confirmed trades | ESPN transactions feed (recent months) plus your own `data/transactions.csv` |
| Birthplace coordinates | Wikidata (cached forever after the first lookup) |

Why not nba_api? stats.nba.com stalls requests from cloud servers and cdn.nba.com returns "Access Denied" there, so ESPN is the main source. Everything is isolated in `app/sources/espn.py`, so another source can be swapped in later.

## Architecture

```
GitHub Actions / daemon (8am ET)
        |
   app.pipeline.run()
        |-- sources/espn.py          schedule, rosters, careers, trades
        |-- sources/geocode.py       birthplace -> coordinates (Wikidata, cached)
        |-- sources/transactions.py  trade confirmation (ESPN + CSV)
        |-- rules.py                 pure detection logic (unit-tested, no network)
        |
   SQLite cache (data/nba.sqlite)  ->  web/data/YYYY-MM-DD.json + index.json
        |
   web/index.html (static dashboard)   or   FastAPI (app.server): /api/slate, /api/slate.csv, /api/health
```

## Detection rules

- **Birthday**: birth month/day equals game date. Feb 29 birthdays are observed on Feb 28 in non-leap years.
- **Hometown**: birthplace within `HOMETOWN_RADIUS_MI` (default 25) of the arena, or of the home team's city when the player is visiting. Manual overrides in `config/overrides.yaml` replace the birthplace and count as high confidence.
- **Revenge**: the opponent franchise is in the player's career history and the player now plays elsewhere.
  - **high**: trade confirmed in the transactions feed or CSV, or a manual flag
  - **medium**: left that team mid-season (likely a trade or waiver)
  - **low**: left between seasons (could be free agency, not a trade)
  - Stints under `MIN_GP_FOR_REVENGE` games are ignored unless a trade is confirmed.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest                # 11 tests, no network needed
python -m app.cli run           # build today's slate (or the next game day)
python -m app.cli serve         # dashboard at http://localhost:8000
```

The first run is slow (about 25 to 40 minutes for a full 12-game night) because it looks up every player's career history and birthplace. Everything is cached, so later runs take about 20 seconds.

```bash
python -m app.cli run --date 2026-11-05 --notify
python -m app.cli import-transactions path/to/trades.csv
python -m app.cli daemon --hour 8      # built-in daily scheduler
```

No API keys are required. Optional notifications: Discord webhook or Telegram bot (see `.env.example`).

## Deployment

- **GitHub Actions (free)**: `.github/workflows/daily.yml` builds the slate each morning and commits `web/data/`. Turn on GitHub Pages for the `web/` folder. Add notification secrets if wanted. The SQLite cache is stored with the Actions cache, so only the first run is slow.
- **Docker**: `docker build -t nba-special . && docker run -p 8000:8000 -v $PWD/data:/app/data nba-special`

## Known limitations

- **Hometown is birthplace, not where someone grew up.** Many players are born in one city and raised in another. Use `config/overrides.yaml` for known cases. High-school location is not detected yet.
- **Trades are confirmed only for recent months.** ESPN's feed covers roughly the last 10 months. Older departures show as medium or low confidence. Add older trades to `data/transactions.csv` to upgrade them.
- **Multi-team seasons**: the "left mid-season" signal assumes ESPN lists a player's teams in the order he played for them. Check a known case if this matters to you.
- **Unofficial feeds**: ESPN and Wikidata have no guarantee of stability. Failures appear in the dashboard's warning banner, and cached data is used when possible.
- **Wikidata misses**: some small towns or international birthplaces are not found, so those players get no hometown flag. Misses are retried monthly.
- **Neutral-site games** use the venue city reported by ESPN.
- **Two-way and 10-day contracts** appear only if ESPN's roster lists them.

## Maintenance

- Check the dashboard's warning banner after runs.
- Refresh `data/transactions.csv` after trade deadlines and the offseason.
- If a feed changes format, the tests in `tests/test_espn.py` show which parser to fix.

## History (player vs player)
`config/rivalries.yaml` lists documented rivalries (reason + source links). A History box shows on a card only when both players are on the two teams that day. Head-to-head stats are computed from ESPN game logs (games where both played, matched by game id) and are never typed in. To add one, give it a short factual reason and at least one source link; entries without both are ignored.
Images are cached in `web/img/` and Basketball-Reference pages are fetched slowly (one every ~3 s), so the first run for a new slate takes a while; later runs use the cache. GitHub's servers may be blocked by Basketball-Reference, in which case revenge confidence falls back to ESPN data.


## NFL board

`python -m app.cli nfl` builds the current NFL week (every game day from today) into `web/data/nfl/`.
It covers quarterbacks, running backs, receivers, tight ends and kickers on the official roster (backups included,
practice squad and injured reserve left out), with the same Revenge / Hometown / Birthday / Holiday / History flags
and position-based matchup grades from real box scores.

- Revenge exits come from ESPN's transaction log (it keeps one log per calendar year, back to about 2015). Only trades
  and releases found in the log are shown as confirmed. If the log has nothing, the card says the exit is not confirmed.
- History boxes need sourced entries in `config/rivalries_nfl.yaml` (none yet).
- Data is cached in `data/nfl.sqlite`; the first build is slow (about 25 minutes), later ones are quick.
