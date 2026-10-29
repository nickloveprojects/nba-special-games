"""Turn a birthplace (city, state/country) into coordinates using Wikidata. Results are cached in SQLite."""
import logging
import time
from datetime import datetime, timezone

from ..net import SourceError, get_json

log = logging.getLogger("nba")
ENDPOINT = "https://query.wikidata.org/sparql"
MISS_TTL_DAYS = 30
US = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
      "CT": "Connecticut", "DE": "Delaware", "DC": "Washington, D.C.", "FL": "Florida", "GA": "Georgia",
      "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
      "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts",
      "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
      "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico",
      "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
      "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
      "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
      "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"}
CA = {"ON": "Ontario", "QC": "Quebec", "BC": "British Columbia", "AB": "Alberta", "MB": "Manitoba"}
COUNTRY = {"USA": "United States of America", "US": "United States of America", "UK": "United Kingdom"}

_state = {"fails": 0}


def reset():
    _state["fails"] = 0


def _q(s: str) -> str:
    return s.replace("\\", "").replace('"', "")


def _query(city, region_label, via_country):
    link = "wdt:P17" if via_country else "wdt:P131+"
    return f"""SELECT ?p ?coord ?pop WHERE {{
  ?p rdfs:label "{_q(city)}"@en ; wdt:P625 ?coord ; wdt:P31/wdt:P279* wd:Q486972 .
  ?p {link} ?r . ?r rdfs:label "{_q(region_label)}"@en .
  OPTIONAL {{ ?p wdt:P1082 ?pop }}
}} ORDER BY DESC(?pop) LIMIT 1"""


def lookup(city: str, state: str, country: str) -> dict | None:
    """Network call: biggest settlement with this name inside the given state/province/country."""
    st = (state or "").strip()
    if st.upper() in US and (not country or country.upper() in ("USA", "US")):
        region, via_country = US[st.upper()], False
    elif st in US.values():
        region, via_country = st, False
    elif st.upper() in CA:
        region, via_country = CA[st.upper()], False
    elif st in CA.values():
        region, via_country = st, False
    elif country:
        region, via_country = COUNTRY.get(country, country), True
    elif st:
        region, via_country = COUNTRY.get(st, st), True   # e.g. high school "in Lagos, Nigeria"
    else:
        return None
    data = get_json(ENDPOINT, params={"query": _query(city, region, via_country), "format": "json"},
                    headers={"Accept": "application/sparql-results+json"}, retries=3, timeout=60)
    rows = data["results"]["bindings"]
    if not rows:
        return None
    b = rows[0]
    lon, lat = b["coord"]["value"][6:-1].split()
    return {"lat": float(lat), "lon": float(lon), "source_url": b["p"]["value"].replace("http://", "https://").replace("/entity/", "/wiki/")}


def get_place(conn, city: str, state: str, country: str) -> dict | None:
    """Cached geocode. Returns {label, lat, lon, source_url} or None. Raises SourceError when Wikidata is down."""
    if not city:
        return None
    key = f"{city}|{state}|{country}".lower()
    r = conn.execute("SELECT * FROM places WHERE key=?", (key,)).fetchone()
    if r:
        age = (datetime.now(timezone.utc).replace(tzinfo=None) - datetime.fromisoformat(r["updated"])).days
        if r["found"] or age < MISS_TTL_DAYS:
            return dict(r) if r["found"] else None
    if _state["fails"] >= 5:
        raise SourceError("Wikidata unavailable (skipped after repeated failures)")
    try:
        time.sleep(0.5)
        g = lookup(city, state, country)
        _state["fails"] = 0
    except SourceError:
        _state["fails"] += 1
        raise
    label = ", ".join(x for x in (city, state or country) if x)
    conn.execute("INSERT OR REPLACE INTO places VALUES(?,?,?,?,?,?,?)",
                 (key, label, g and g["lat"], g and g["lon"], g and g["source_url"], int(bool(g)),
                  datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")))
    conn.commit()
    return {"label": label, **g} if g else None
