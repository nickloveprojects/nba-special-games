import csv
import io
import json

from . import config


def write_slate(slate: dict):
    config.OUT.mkdir(parents=True, exist_ok=True)
    (config.OUT / f"{slate['date']}.json").write_text(json.dumps(slate, indent=1))
    dates = sorted({p.stem for p in config.OUT.glob("????-??-??.json")}, reverse=True)
    (config.OUT / "index.json").write_text(json.dumps({"dates": dates, "latest": dates[0]}))


def finalize(dates: list[str]):
    """Keep only the given days (today and tomorrow): delete older/other slate files and rewrite the index.
    The first date is the default shown on the site."""
    keep = sorted(set(dates))
    for p in config.OUT.glob("????-??-??.json"):
        if p.stem not in keep:
            p.unlink()
    (config.OUT / "index.json").write_text(json.dumps({"dates": keep, "latest": keep[0]}))


def to_csv(slate: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["date", "player", "team", "opponent", "home_away", "tip", "arena", "location",
                "categories", "details", "confidence", "pts", "reb", "ast"])
    for e in slate["entries"]:
        s = e.get("stats") or {}
        w.writerow([slate["date"], e["name"], e["team"], e["opponent"], e["home_away"], e["tip"], e["arena"],
                    e["location"], "/".join(e["categories"]), " | ".join(t["detail"] for t in e["tags"]),
                    "/".join(t["confidence"] for t in e["tags"]), s.get("pts", ""), s.get("reb", ""),
                    s.get("ast", "")])
    return buf.getvalue()


def to_text(slate: dict, limit=25) -> str:
    lines = [f"Backstory Sports NBA, {slate['date']} ({slate['games']} games, {len(slate['entries'])} flagged)"]
    for e in slate["entries"][:limit]:
        lines.append(f"- {e['name']} ({e['team']} {'vs' if e['home_away'] == 'home' else '@'} {e['opponent']}, "
                     f"{e['tip']}) [{', '.join(e['categories'])}]: " + "; ".join(t["detail"] for t in e["tags"]))
    if len(slate["entries"]) > limit:
        lines.append(f"...and {len(slate['entries']) - limit} more")
    if slate["warnings"]:
        lines.append(f"Warnings: {len(slate['warnings'])} (see dashboard)")
    return "\n".join(lines)
