"""Kickoff weather for outdoor games, from Open-Meteo (free, no key). Indoor stadiums are reported as indoors.
Only temperature, wind and rain chance are used. A failed lookup is simply left blank."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from .net import SourceError, get_json

log = logging.getLogger("nba")
URL = "https://api.open-meteo.com/v1/forecast"


def pick(hourly: dict, tip_utc: str) -> dict | None:
    """The forecast hour closest to kickoff, from an Open-Meteo hourly block."""
    times = hourly.get("time") or []
    if not times:
        return None
    tip = datetime.fromisoformat(tip_utc).astimezone(timezone.utc).replace(tzinfo=None)
    i = min(range(len(times)), key=lambda k: abs(datetime.fromisoformat(times[k]) - tip))
    g = lambda k: (hourly.get(k) or [None] * len(times))[i]  # noqa: E731
    temp, wind, gust, rain = g("temperature_2m"), g("wind_speed_10m"), g("wind_gusts_10m"), g("precipitation_probability")
    if temp is None or wind is None:
        return None
    return {"indoor": False, "temp": round(temp), "wind": round(wind), "gust": round(gust) if gust is not None else None,
            "rain": round(rain) if rain is not None else None}


def forecast(lat: float, lon: float, tip_utc: str, indoor: bool = False) -> dict | None:
    if indoor:
        return {"indoor": True}
    try:
        data = get_json(URL, params={
            "latitude": lat, "longitude": lon, "timezone": "UTC", "forecast_days": 10,
            "temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
            "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,wind_gusts_10m"}, retries=3, timeout=20)
        return pick(data.get("hourly") or {}, tip_utc)
    except (SourceError, ValueError, KeyError) as e:
        log.warning("weather unavailable: %s", e)
        return None


def label(w: dict | None) -> str:
    if not w:
        return ""
    if w.get("indoor"):
        return "Indoors"
    s = f"{w['temp']}°F, wind {w['wind']} mph"
    if w.get("rain") is not None and w["rain"] >= 30:
        s += f", {w['rain']}% rain"
    return s


def passing_factor(w: dict | None) -> float:
    """Backtested on 2024-26 games: 15+ mph wind cut team passing about 15%, cold (under 40F) about 7%.
    The adjustment is applied to passing and receiving stats only; rushing showed no reliable change."""
    if not w or w.get("indoor"):
        return 1.0
    f = 1.0
    if w["wind"] >= 15:
        f *= 0.88
    elif w["wind"] >= 8:
        f *= 0.97
    if w["temp"] < 40:
        f *= 0.95
    return f
