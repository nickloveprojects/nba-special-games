"""Download small team logos and player headshots once, so the page works without hot-linking ESPN."""
import logging
import time

import requests

from .. import config
from ..teams_geo import LOGO_KEY

log = logging.getLogger("nba")
HDR = {"User-Agent": "Mozilla/5.0 (compatible; nba-special-games)"}
COMBINER = "https://a.espncdn.com/combiner/i?img="


def _save(url: str, path, max_age_days: float | None = None) -> bool:
    if path.exists() and path.stat().st_size > 500:
        if max_age_days is None or (time.time() - path.stat().st_mtime) < max_age_days * 86400:
            return True
    try:
        r = requests.get(url, headers=HDR, timeout=25)
        if r.status_code != 200 or len(r.content) < 500:
            return False
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(r.content)
        return True
    except requests.RequestException as e:
        log.warning("image %s failed: %s", url, e)
        return False


def team_logo(abbr: str) -> str | None:
    key = LOGO_KEY.get(abbr)
    if not key:
        return None
    ok = _save(f"{COMBINER}/i/teamlogos/nba/500/{key}.png&w=96&h=96", config.IMG / "teams" / f"{abbr}.png")
    return f"img/teams/{abbr}.png" if ok else None


def headshot(player_id: int) -> str | None:
    ok = _save(f"{COMBINER}/i/headshots/nba/players/full/{player_id}.png&w=160&h=116",
               config.IMG / "players" / f"{player_id}.png", max_age_days=30)
    return f"img/players/{player_id}.png" if ok else None
