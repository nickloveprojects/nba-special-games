"""Career special-game summaries, computed only from real game logs (never estimated).
Each line says how many earlier games fit the situation and the player's averages in them."""
import math
from datetime import date, timedelta

from . import config, rules
from .teams_geo import ABBR_TO_ID, TEAMS


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    d = date(year, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


HOLIDAYS = {   # name -> function(year) -> date
    "Christmas": lambda y: date(y, 12, 25),
    "New Year's Day": lambda y: date(y, 1, 1),
    "MLK Day": lambda y: nth_weekday(y, 1, 0, 3),
    "Valentine's Day": lambda y: date(y, 2, 14),
    "Halloween": lambda y: date(y, 10, 31),
    "Thanksgiving": lambda y: nth_weekday(y, 11, 3, 4),
}


def holiday_name(d: date) -> str | None:
    return next((n for n, f in HOLIDAYS.items() if f(d.year) == d), None)


def avg(rows: list[dict]) -> dict:
    n = len(rows)
    f = lambda k: round(sum(r[k] for r in rows) / n, 1)  # noqa: E731
    return {"n": n, "pts": f("pts"), "reb": f("reb"), "ast": f("ast")}


def _times(n: int) -> str:
    return "1 time" if n == 1 else f"{n} times"


def _stats(a: dict) -> str:
    return f"avg {a['pts']} pts, {a['reb']} reb, {a['ast']} ast"


def birthday_games(logs: list[dict], birth: date) -> list[dict]:
    return [g for g in logs if g["date"][5:] == f"{birth.month:02d}-{birth.day:02d}"]


def hometown_games(logs: list[dict], lat: float, lon: float, radius: float) -> list[dict]:
    out = []
    for g in logs:
        tid = ABBR_TO_ID.get(g.get("venue") or "")
        if tid and rules.haversine_mi(lat, lon, TEAMS[tid][2], TEAMS[tid][3]) <= radius:
            out.append(g)
    return out


def holiday_games(logs: list[dict], name: str) -> list[dict]:
    f = HOLIDAYS[name]
    return [g for g in logs if f(int(g["date"][:4])).isoformat() == g["date"]]


def lines(logs: list[dict], slate_date: date, birth: date | None, tags: list[dict], opp: str, opp_name: str) -> list[dict]:
    """logs: every known game before `slate_date`. tags: the player's tags (with the private _place/_exit fields)."""
    past = [g for g in logs if g["date"] < slate_date.isoformat()]
    out = []

    def add(kind, label, text, rows, scope=""):
        if rows:
            a = avg(rows)
            out.append({"kind": kind, "label": label, "text": text.format(n=_times(a["n"]), s=_stats(a)), **a, "scope": scope})

    for t in tags:
        c = t["category"]
        if c == "Birthday" and birth:
            add("birthday", "Birthday", "Has played on his birthday {n} ({s}).", birthday_games(past, birth))
        elif c == "Hometown" and t.get("_place"):
            add("hometown", "Hometown", "Has played in his hometown area {n} ({s}).",
                hometown_games(past, *t["_place"], config.HOMETOWN_RADIUS_MI))
        elif c == "History" and t.get("h2h") and t["h2h"]["games"]:
            h = t["h2h"]
            m = h["me"]
            out.append({"kind": "history", "label": "Rivalry", "n": h["games"], "pts": m["pts"], "reb": m["reb"], "ast": m["ast"],
                        "text": f"Has faced {t['with']} {_times(h['games'])} (avg {m['pts']} pts, {m['reb']} reb, {m['ast']} ast).",
                        "scope": h["scope"]})
        elif c == "Revenge" and t.get("_exit"):
            add("revenge", "Revenge", f"Has faced the {opp_name} {{n}} since leaving them ({{s}}).",
                [g for g in past if g["opp"] == opp and g["date"] > t["_exit"]])
    hol = holiday_name(slate_date)
    if hol:
        add("holiday", "Holiday", f"Has played on {hol} {{n}} ({{s}}).", holiday_games(past, hol))
    return out
