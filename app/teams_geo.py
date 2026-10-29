"""Static NBA team table: id -> (abbr, city label, arena lat, arena lon).
Used for hometown distance checks. IDs are stable across relocations (SEA->OKC, NJN->BKN)."""

TEAMS = {
    1610612737: ("ATL", "Atlanta", 33.757, -84.396),
    1610612738: ("BOS", "Boston", 42.366, -71.062),
    1610612739: ("CLE", "Cleveland", 41.496, -81.688),
    1610612740: ("NOP", "New Orleans", 29.949, -90.082),
    1610612741: ("CHI", "Chicago", 41.881, -87.674),
    1610612742: ("DAL", "Dallas", 32.790, -96.810),
    1610612743: ("DEN", "Denver", 39.749, -105.008),
    1610612744: ("GSW", "San Francisco", 37.768, -122.388),
    1610612745: ("HOU", "Houston", 29.751, -95.362),
    1610612746: ("LAC", "Los Angeles", 33.944, -118.341),
    1610612747: ("LAL", "Los Angeles", 34.043, -118.267),
    1610612748: ("MIA", "Miami", 25.781, -80.187),
    1610612749: ("MIL", "Milwaukee", 43.045, -87.917),
    1610612750: ("MIN", "Minneapolis", 44.980, -93.276),
    1610612751: ("BKN", "Brooklyn", 40.683, -73.975),
    1610612752: ("NYK", "New York", 40.751, -73.994),
    1610612753: ("ORL", "Orlando", 28.539, -81.384),
    1610612754: ("IND", "Indianapolis", 39.764, -86.156),
    1610612755: ("PHI", "Philadelphia", 39.901, -75.172),
    1610612756: ("PHX", "Phoenix", 33.446, -112.071),
    1610612757: ("POR", "Portland", 45.532, -122.667),
    1610612758: ("SAC", "Sacramento", 38.580, -121.500),
    1610612759: ("SAS", "San Antonio", 29.427, -98.437),
    1610612760: ("OKC", "Oklahoma City", 35.463, -97.515),
    1610612761: ("TOR", "Toronto", 43.643, -79.379),
    1610612762: ("UTA", "Salt Lake City", 40.768, -111.901),
    1610612763: ("MEM", "Memphis", 35.138, -90.051),
    1610612764: ("WAS", "Washington", 38.898, -77.021),
    1610612765: ("DET", "Detroit", 42.341, -83.055),
    1610612766: ("CHA", "Charlotte", 35.225, -80.839),
}
ABBR_TO_ID = {v[0]: k for k, v in TEAMS.items()}
ALIASES = {"NJN": "BKN", "BRK": "BKN", "NOH": "NOP", "NOK": "NOP", "NO": "NOP", "SEA": "OKC",
           "CHO": "CHA", "CHH": "CHA", "PHO": "PHX", "GS": "GSW", "NY": "NYK", "SA": "SAS",
           "VAN": "MEM", "WSB": "WAS", "WSH": "WAS", "UTAH": "UTA", "NJ": "BKN"}


def team_id(token) -> int | None:
    """Resolve an abbreviation/alias/int to a team id."""
    if token is None:
        return None
    t = str(token).strip().upper()
    if t.isdigit():
        return int(t) if int(t) in TEAMS else None
    return ABBR_TO_ID.get(ALIASES.get(t, t))


def abbr(tid: int) -> str:
    return TEAMS[tid][0] if tid in TEAMS else str(tid)


NICK = {"ATL": "Hawks", "BOS": "Celtics", "BKN": "Nets", "CHA": "Hornets", "CHI": "Bulls", "CLE": "Cavaliers",
        "DAL": "Mavericks", "DEN": "Nuggets", "DET": "Pistons", "GSW": "Warriors", "HOU": "Rockets",
        "IND": "Pacers", "LAC": "Clippers", "LAL": "Lakers", "MEM": "Grizzlies", "MIA": "Heat", "MIL": "Bucks",
        "MIN": "Timberwolves", "NOP": "Pelicans", "NYK": "Knicks", "OKC": "Thunder", "ORL": "Magic",
        "PHI": "76ers", "PHX": "Suns", "POR": "Trail Blazers", "SAC": "Kings", "SAS": "Spurs", "TOR": "Raptors",
        "UTA": "Jazz", "WAS": "Wizards"}
# file name ESPN uses for each team logo
LOGO_KEY = {"ATL": "atl", "BOS": "bos", "BKN": "bkn", "CHA": "cha", "CHI": "chi", "CLE": "cle", "DAL": "dal",
            "DEN": "den", "DET": "det", "GSW": "gs", "HOU": "hou", "IND": "ind", "LAC": "lac", "LAL": "lal",
            "MEM": "mem", "MIA": "mia", "MIL": "mil", "MIN": "min", "NOP": "no", "NYK": "ny", "OKC": "okc",
            "ORL": "orl", "PHI": "phi", "PHX": "phx", "POR": "por", "SAC": "sac", "SAS": "sa", "TOR": "tor",
            "UTA": "utah", "WAS": "wsh"}


def nick(tid_or_abbr) -> str:
    a = abbr(tid_or_abbr) if isinstance(tid_or_abbr, int) else tid_or_abbr
    return NICK.get(a, a)
