"""Record chases: active streaks computed from ESPN game logs, measured against all-time marks in config/records.yaml.

The streak engine is pure (no network) so it is unit-tested; nfl.build_slates feeds it the logs it already fetches."""
import logging

import yaml

from . import config

log = logging.getLogger("nba")
PATH = config.ROOT / "config" / "records.yaml"


def load(sport: str) -> list[dict]:
    try:
        rows = (yaml.safe_load(PATH.read_text()) or {}).get("records") or []
    except FileNotFoundError:
        return []
    return [r for r in rows if r.get("sport") == sport and r.get("sources") and r.get("record") and r.get("fields")]


def active_streak(logs: list[dict], fields: list[str], threshold: float) -> tuple[int, list[dict]]:
    """The run of consecutive most-recent games (date order) where the summed fields reach the threshold."""
    run = []
    for g in sorted(logs, key=lambda x: x["date"]):
        if sum(float(g["row"].get(f, 0) or 0) for f in fields) >= threshold:
            run.append(g)
        else:
            run = []
    return len(run), run


def chase(rec: dict, player: dict, logs: list[dict], opp: str, tip: str, day: str, team: str) -> dict | None:
    """One flag, or None when this player's streak isn't close enough to the record."""
    if player["pos"] not in rec["positions"]:
        return None
    n, games = active_streak([g for g in logs if g["date"] < day], rec["fields"], rec["threshold"])
    if n < rec["record"] - rec.get("show_within", 1):
        return None
    if n > rec["record"]:
        status, line = "extends", f"Owns the record at {n}; another game extends it."
    elif n == rec["record"]:
        status, line = "break", f"Tied the record at {n}; one more game breaks it."
    else:
        status, line = "tie", f"At {n}; one more game ties the record of {rec['record']}."
    return {"record_id": rec["id"], "title": rec["title"], "short": rec["short"], "status": status, "line": line,
            "player_id": player["id"], "name": player["name"], "team": team, "opponent": opp, "tip": tip, "date": day,
            "current": n, "record": rec["record"], "threshold": rec["threshold"], "holders": rec["holders"],
            "sources": rec["sources"],
            "games": [{"date": g["date"], "opp": g["opp"], "home": g["home"], "result": g["result"],
                       "total": sum(float(g["row"].get(f, 0) or 0) for f in rec["fields"])} for g in games[-8:]]}
