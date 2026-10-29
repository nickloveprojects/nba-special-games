"""Basketball-Reference: where a player went to high school, and his full transaction log
(trades, waivers, free-agent signings). Used to confirm HOW a player left a team.

Polite by design: one request every 3.3 seconds (their robots.txt asks for 3), every page cached in SQLite,
a per-run page budget, and a circuit breaker that stops after repeated failures so the rest of the app
keeps working with ESPN data."""
import html as htmllib
import json
import logging
import re
import time
from datetime import date, datetime, timezone

import requests

from .. import config
from ..net import NotFound, SourceError
from ..rules import name_similarity, norm_name

log = logging.getLogger("nba")
BASE = "https://www.basketball-reference.com"
UA = "Mozilla/5.0 (compatible; nba-special-games personal project)"
MIN_GAP = 3.3
_state = {"last": 0.0, "fails": 0, "pages": 0}


def reset():
    _state.update(last=0.0, fails=0, pages=0)


def _fetch(path: str) -> str:
    if _state["fails"] >= 3:
        raise SourceError("Basketball-Reference unavailable (skipped after repeated failures)")
    if _state["pages"] >= config.BBREF_MAX_PAGES:
        raise SourceError("Basketball-Reference page budget for this run reached (rest loads on the next run)")
    wait = MIN_GAP - (time.time() - _state["last"])
    if wait > 0:
        time.sleep(wait)
    try:
        r = requests.get(BASE + path, headers={"User-Agent": UA}, timeout=40)
    except requests.RequestException as e:
        _state["last"] = time.time()
        _state["fails"] += 1
        raise SourceError(f"Basketball-Reference {path}: {e}") from e
    _state["last"] = time.time()
    if r.status_code == 404:
        raise NotFound(f"Basketball-Reference {path}: not found")
    if r.status_code in (403, 429) or r.status_code >= 500:
        _state["fails"] += 1
        raise SourceError(f"Basketball-Reference {path}: HTTP {r.status_code}")
    _state["fails"] = 0
    _state["pages"] += 1
    r.encoding = "utf-8"
    return r.text


def _clean(fragment: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", "", fragment))).strip()


def _now() -> str:
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")


def _age_days(ts) -> float:
    if not ts:
        return 10 ** 6
    return (datetime.now(timezone.utc).replace(tzinfo=None) - datetime.fromisoformat(ts)).total_seconds() / 86400


# ------------------------------------------------------------------ player index
ROW = re.compile(r'<th[^>]*data-append-csv="(?P<slug>[a-z0-9]+)"[^>]*data-stat="player"[^>]*>(?P<name>.*?)</th>'
                 r'(?P<rest>.*?)</tr>', re.S)


def parse_index(page: str) -> list[dict]:
    out = []
    for m in ROW.finditer(page):
        rest = m.group("rest")
        ym = re.search(r'data-stat="year_max"[^>]*>(\d{4})', rest)
        bm = re.search(r'data-stat="birth_date"[^>]*csk="(\d{4})(\d{2})(\d{2})"', rest)
        out.append({"slug": m.group("slug"), "name": _clean(m.group("name")),
                    "year_max": int(ym.group(1)) if ym else 0,
                    "birth": f"{bm.group(1)}-{bm.group(2)}-{bm.group(3)}" if bm else ""})
    return out


def _letters(name: str) -> list[str]:
    toks = norm_name(name).split()
    letters = []
    for t in (toks[-1:] + toks[-2:-1]):
        if t and t[0].isalpha() and t[0] not in letters:
            letters.append(t[0])
    return letters


def _ensure_letter(conn, letter: str):
    r = conn.execute("SELECT fetched FROM bbref_letters WHERE letter=?", (letter,)).fetchone()
    if r and _age_days(r["fetched"]) < 14:
        return
    rows = parse_index(_fetch(f"/players/{letter}/"))
    keep_from = date.today().year - 1
    conn.execute("DELETE FROM bbref_index WHERE letter=?", (letter,))
    for p in rows:
        if p["year_max"] >= keep_from:
            conn.execute("INSERT OR REPLACE INTO bbref_index VALUES(?,?,?,?,?)",
                         (p["slug"], p["name"], p["birth"], p["year_max"], letter))
    conn.execute("INSERT OR REPLACE INTO bbref_letters VALUES(?,?)", (letter, _now()))
    conn.commit()


def find_slug(conn, name: str, birth: date | None) -> str | None:
    for letter in _letters(name):
        _ensure_letter(conn, letter)
        best, best_score = None, 0.0
        for r in conn.execute("SELECT slug,name,birth FROM bbref_index WHERE letter=?", (letter,)):
            score = name_similarity(name, r["name"])
            if birth and r["birth"] == birth.isoformat():
                score += 0.5          # exact birth date is the strongest signal
            elif birth and r["birth"]:
                continue              # different birth date: a different person
            if score > best_score:
                best, best_score = r["slug"], score
        if best and best_score >= 0.6:
            return best
    return None


# ----------------------------------------------------------------- player page
def parse_hs(text: str) -> list[dict]:
    """'DeMatha Catholic in Hyattsville, Maryland' -> [{school, city, region}]"""
    out = []
    for m in re.finditer(r"(?P<school>[^,;]+?) in (?P<city>[^,;]+), (?P<region>[A-Za-z. ]+?)(?=$|,|;| and )", text):
        out.append({"school": m.group("school").strip(), "city": m.group("city").strip(),
                    "region": m.group("region").strip()})
    return out


def _tx_kind(low: str) -> str:
    if low.startswith("drafted"):
        return "draft"
    if low.startswith("traded by") or (low.startswith("as part of") and "traded by" in low[:80]):
        return "trade"
    if low.startswith("waived") or low.startswith("released"):
        return "waive"
    if low.startswith("claimed"):
        return "claim"
    if low.startswith("signed as a free agent"):
        return "fa_sign"
    if low.startswith("signed") and "extension" not in low[:40]:
        return "sign"
    return "other"


def parse_player(page: str) -> dict:
    hs = []
    m = re.search(r"High School:\s*</strong>(.*?)</p>", page, re.S)
    if m:
        hs = parse_hs(_clean(m.group(1)))
    txs = []
    for p in re.finditer(r'<p class="transaction[^"]*">\s*<strong>(.*?)</strong>:\s*(.*?)</p>', page, re.S):
        try:
            d = datetime.strptime(_clean(p.group(1)), "%B %d, %Y").date().isoformat()
        except ValueError:
            continue
        text = _clean(p.group(2))
        kind = _tx_kind(text.lower())
        if kind == "other":
            continue
        txs.append({"date": d, "kind": kind, "text": text,
                    "teams": re.findall(r'href="/teams/([A-Z]{3})/', p.group(2))})
    return {"high_schools": hs, "transactions": txs}


def profile(conn, player_id: int, name: str, birth: date | None, need_tx=True):
    """Cached profile {slug, high_schools, transactions} or None when the player can't be found.
    Raises SourceError when Basketball-Reference can't be reached (callers degrade to ESPN data)."""
    row = conn.execute("SELECT * FROM bbref_profiles WHERE player_id=?", (player_id,)).fetchone()
    if row and row["found"]:
        if not need_tx or _age_days(row["fetched"]) < config.BBREF_TX_TTL_DAYS:
            return {"slug": row["slug"], "high_schools": json.loads(row["hs_json"]),
                    "transactions": json.loads(row["tx_json"])}
    elif row and _age_days(row["fetched"]) < 30:
        return None
    slug = (row["slug"] if row and row["slug"] else None) or find_slug(conn, name, birth)
    if not slug:
        conn.execute("INSERT OR REPLACE INTO bbref_profiles VALUES(?,?,?,?,?,?)",
                     (player_id, None, "[]", "[]", _now(), 0))
        conn.commit()
        return None
    try:
        data = parse_player(_fetch(f"/players/{slug[0]}/{slug}.html"))
    except NotFound:
        conn.execute("INSERT OR REPLACE INTO bbref_profiles VALUES(?,?,?,?,?,?)",
                     (player_id, slug, "[]", "[]", _now(), 0))
        conn.commit()
        return None
    conn.execute("INSERT OR REPLACE INTO bbref_profiles VALUES(?,?,?,?,?,?)",
                 (player_id, slug, json.dumps(data["high_schools"]), json.dumps(data["transactions"]), _now(), 1))
    conn.commit()
    return {"slug": slug, **data}
