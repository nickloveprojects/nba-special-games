import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS players(
  player_id INTEGER PRIMARY KEY, name TEXT, birth_date TEXT, birth_city TEXT, birth_state TEXT,
  birth_country TEXT, team_id INTEGER, school TEXT, last_seen TEXT, career_fetched TEXT, career_last_team INTEGER);
CREATE TABLE IF NOT EXISTS places(              -- geocoded birthplaces / arena cities (cached from Wikidata)
  key TEXT PRIMARY KEY, label TEXT, lat REAL, lon REAL, source_url TEXT, found INTEGER, updated TEXT);
CREATE TABLE IF NOT EXISTS stints(              -- per franchise, derived from career history
  player_id INTEGER, team_id INTEGER, abbr TEXT, first_season TEXT, last_season TEXT, gp INTEGER,
  left_midseason INTEGER, left_year INTEGER, PRIMARY KEY(player_id, team_id));
CREATE TABLE IF NOT EXISTS season_stats(
  player_id INTEGER, season TEXT, gp INTEGER, min REAL, pts REAL, reb REAL, ast REAL,
  PRIMARY KEY(player_id, season));
CREATE TABLE IF NOT EXISTS transactions(        -- trades from ESPN + your CSV; confirms revenge
  id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, player_name TEXT, from_team_id INTEGER,
  to_team_id INTEGER, type TEXT, source TEXT,
  UNIQUE(date, player_name, from_team_id, to_team_id, type));
CREATE TABLE IF NOT EXISTS games(
  game_id TEXT PRIMARY KEY, game_date TEXT, tip_utc TEXT, home_id INTEGER, away_id INTEGER, arena TEXT);
CREATE TABLE IF NOT EXISTS flags(               -- every tag ever produced (history / analysis)
  game_date TEXT, game_id TEXT, player_id INTEGER, category TEXT, detail TEXT, confidence TEXT,
  PRIMARY KEY(game_date, game_id, player_id, category));
CREATE TABLE IF NOT EXISTS bbref_index(        -- Basketball-Reference player index (slug lookup)
  slug TEXT PRIMARY KEY, name TEXT, birth TEXT, year_max INTEGER, letter TEXT);
CREATE TABLE IF NOT EXISTS bbref_letters(letter TEXT PRIMARY KEY, fetched TEXT);
CREATE TABLE IF NOT EXISTS bbref_profiles(      -- high schools + transaction log per player
  player_id INTEGER PRIMARY KEY, slug TEXT, hs_json TEXT, tx_json TEXT, fetched TEXT, found INTEGER);
CREATE TABLE IF NOT EXISTS gamelog(             -- compact per-season game logs
  player_id INTEGER, end_year INTEGER, fetched TEXT, json TEXT, PRIMARY KEY(player_id, end_year));
CREATE TABLE IF NOT EXISTS runs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, started TEXT, finished TEXT, slate_date TEXT,
  status TEXT, warnings TEXT);
"""


def connect() -> sqlite3.Connection:
    config.DATA.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript(SCHEMA)
    return c
