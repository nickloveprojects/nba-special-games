import os
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("NBA_DATA_DIR", ROOT / "data"))
OUT = Path(os.getenv("NBA_OUT_DIR", ROOT / "web" / "data"))
WEB = ROOT / "web"
IMG = Path(os.getenv("NBA_IMG_DIR", WEB / "img"))
DB_PATH = DATA / "nba.sqlite"
OVERRIDES = ROOT / "config" / "overrides.yaml"
TRANSACTIONS_CSV = DATA / "transactions.csv"

TZ = os.getenv("TIMEZONE", "America/New_York")

SLEEP = float(os.getenv("NBA_SLEEP", "0.25"))
RETRIES = int(os.getenv("NBA_RETRIES", "4"))
TIMEOUT = int(os.getenv("NBA_TIMEOUT", "30"))
HOMETOWN_RADIUS_MI = float(os.getenv("HOMETOWN_RADIUS_MI", "25"))
MIN_GP_FOR_REVENGE = int(os.getenv("MIN_GP_FOR_REVENGE", "15"))
CAREER_TTL_DAYS = int(os.getenv("CAREER_TTL_DAYS", "3"))
GEO_TTL_DAYS = 365          # found birthplaces rarely change
GEO_MISS_TTL_DAYS = 30      # retry unmatched players monthly


def current_end_year(today: date | None = None) -> int:
    """ESPN labels a season by the year it ends (2026-27 -> 2027)."""
    t = today or date.today()
    return (t.year if t.month >= 10 else t.year - 1) + 1


def current_season(today: date | None = None) -> str:
    """NBA season string, e.g. 2026-27 (season flips in October)."""
    t = today or date.today()
    y = t.year if t.month >= 10 else t.year - 1
    return f"{y}-{str(y + 1)[2:]}"


# Basketball-Reference (high schools + full transaction logs). Their robots.txt asks for >=3s between requests.
BBREF_ENABLED = os.getenv("BBREF_ENABLED", "1") != "0"
BBREF_MAX_PAGES = int(os.getenv("BBREF_MAX_PAGES", "700"))   # per run; the rest is picked up on the next run
BBREF_TX_TTL_DAYS = int(os.getenv("BBREF_TX_TTL_DAYS", "3"))
GAMELOG_TTL_HOURS = int(os.getenv("GAMELOG_TTL_HOURS", "6"))
