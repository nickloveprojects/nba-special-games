"""Milestone flags: a player close to passing someone on an all-time NBA list, or to a round career number.

Career totals come from ESPN every build. The all-time lists (config/alltime.yaml) hold each source's published
numbers for retired players, which never change; active players on a list are refreshed from ESPN so a rank is never
computed from a stale total. Regular season only, which is what the record books count."""
import logging
from functools import lru_cache

import yaml

from . import config
from .net import NotFound
from .rules import norm_name

log = logging.getLogger("nba")
LISTS_PATH = config.ROOT / "config" / "alltime.yaml"

# How close counts as "within reach". Past this, the flag is noise.
REACH = {"pts": 45, "fgm": 16}
ROUND = {"pts": (1000, 5000), "fgm": (1000, 2000)}  # (step, minimum career total before round numbers matter)


def ordinal(n: int) -> str:
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def parse_totals(data: dict):
    """ESPN athlete stats JSON -> {'pts': int, 'fgm': int} for the regular-season career, or None."""
    cat = next((c for c in data.get("categories", []) if c.get("name") == "totals"), None)
    if not cat or not cat.get("totals"):
        return None
    vals = dict(zip(cat["labels"], cat["totals"]))
    try:
        return {"fgm": int(str(vals["FG"]).split("-")[0].replace(",", "")),
                "pts": int(str(vals["PTS"]).replace(",", ""))}
    except (KeyError, ValueError):
        return None


def load_lists() -> dict:
    return yaml.safe_load(LISTS_PATH.read_text()) or {}


@lru_cache(maxsize=None)
def _fetch(player_id: int):
    from .sources import espn
    try:
        return parse_totals(espn._get(f"{espn.WEB}/athletes/{player_id}/stats"))
    except NotFound:
        return None
    except Exception as exc:  # a failed lookup must never break the build; the flag just doesn't show
        log.warning("career totals failed for %s: %s", player_id, exc)
        return None


def totals(player_id: int):
    return _fetch(int(player_id))


def live_rows(lists: dict, stat: str, fetch=totals) -> list[dict]:
    """The list for one stat, with active players' totals replaced by today's ESPN number. Highest first."""
    rows = []
    for r in lists[stat]["rows"]:
        total = r["total"]
        if r.get("espn_id"):
            t = fetch(r["espn_id"])
            if t:
                total = t[stat]
        rows.append({"name": r["name"], "key": norm_name(r["name"]), "total": total})
    return sorted(rows, key=lambda r: -r["total"])


def tags_for(name: str, tot: dict | None, lists: dict, fetch=totals) -> list[dict]:
    if not tot or not lists:
        return []
    me, out = norm_name(name), []
    for stat, spec in lists.items():
        if stat not in tot:
            continue
        have, need_cap = tot[stat], REACH[stat]
        rows = live_rows(lists, stat, fetch)
        src = [{"label": spec["source"]["label"], "url": spec["source"]["url"]}]
        # 1) passing someone on the all-time list
        others = [r for r in rows if r["key"] != me]
        ahead = [r for r in others if r["total"] >= have]
        if ahead:
            nxt = ahead[-1]                      # closest player at or above him
            # passing nxt puts him just above him: his new rank is nxt's current rank (ties share the better rank)
            rank_if_passed = len([r for r in others if r["total"] > nxt["total"]]) + 1
            needed = nxt["total"] - have + 1
            if needed <= need_cap and rank_if_passed <= len(rows):
                now_rank = len([r for r in others if r["total"] > have]) + 1
                if now_rank <= len(rows):
                    tag = (f"Needs {needed} {spec['short']} to pass {nxt['name']} for {ordinal(rank_if_passed)} "
                           f"on the all-time {spec['label']} list.")
                else:
                    tag = (f"Needs {needed} {spec['short']} to pass {nxt['name']} and enter the all-time "
                           f"top {len(rows)} in {spec['label']}.")
                    rank_if_passed = len(rows)
                out.append({"category": "Milestone", "kind": "rank", "stat": stat, "confidence": "high",
                            "headline": tag, "needed": needed, "current": have,
                            "detail": f"{name} has {have:,} career regular-season {spec['label']}; {nxt['name']} has "
                                      f"{nxt['total']:,}. Totals are through the last finished game.",
                            "sources": src + [{"label": "ESPN career totals",
                                               "url": "https://www.espn.com/nba/"}],
                            "_score": 60 - 3 * rank_if_passed if rank_if_passed <= 10 else 25})
        # 2) round career number
        step, floor = ROUND[stat]
        if have >= floor:
            target = (have // step + 1) * step
            needed = target - have
            if needed <= need_cap:
                out.append({"category": "Milestone", "kind": "round", "stat": stat, "confidence": "high",
                            "headline": f"Needs {needed} {spec['short']} to reach {target:,} career {spec['label']}.",
                            "needed": needed, "current": have,
                            "detail": f"{name} has {have:,} career regular-season {spec['label']}. "
                                      f"Totals are through the last finished game.",
                            "sources": [{"label": "ESPN career totals", "url": "https://www.espn.com/nba/"}],
                            "_score": 20})
    return sorted(out, key=lambda t: -t["_score"])[:2]
