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


def forecast_many(games: list[dict]) -> dict:
    """games: [{"id", "lat", "lon", "tip_utc", "indoor"}] -> {id: forecast or None}. One request covers every outdoor game."""
    out = {g["id"]: ({"indoor": True, "roof": g.get("roof") or "fixed"} if g["indoor"] else None) for g in games}
    wet = [g for g in games if not g["indoor"]]
    if not wet:
        return out
    try:
        data = get_json(URL, params={
            "latitude": ",".join(str(g["lat"]) for g in wet), "longitude": ",".join(str(g["lon"]) for g in wet),
            "timezone": "UTC", "forecast_days": 10, "temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
            "hourly": "temperature_2m,precipitation_probability,wind_speed_10m,wind_gusts_10m"}, retries=3, timeout=30)
        blocks = data if isinstance(data, list) else [data]
        for g, blk in zip(wet, blocks):
            out[g["id"]] = pick(blk.get("hourly") or {}, g["tip_utc"])
    except (SourceError, ValueError, KeyError, TypeError) as e:
        log.warning("weather unavailable: %s", e)
    return out


ROOF_LABEL = {"fixed": "Indoors", "canopy": "Covered, open sides: not adjusted",
              "retractable": "Retractable roof, open or closed unknown: not adjusted"}


def label(w: dict | None) -> str:
    if not w:
        return ""
    if w.get("indoor"):
        return ROOF_LABEL.get(w.get("roof") or "fixed", "Indoors")
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


# ------------------------------------------------------------------ full game report
WMO = {0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog", 51: "Light drizzle", 53: "Drizzle",
       55: "Heavy drizzle", 56: "Freezing drizzle", 57: "Freezing drizzle", 61: "Light rain", 63: "Rain", 65: "Heavy rain",
       66: "Freezing rain", 67: "Freezing rain", 71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
       80: "Light showers", 81: "Showers", 82: "Heavy showers", 85: "Snow showers", 86: "Heavy snow showers",
       95: "Thunderstorms", 96: "Thunderstorms with hail", 99: "Thunderstorms with hail"}
POINTS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def condition(code, rain, cloud) -> str:
    """Model weather code in words. A precipitation code with a low rain chance is shown as sky cover instead,
    so a 1% chance never reads as drizzle."""
    if code is not None and code >= 51 and (rain is None or rain < 30):
        code = 0 if (cloud or 0) < 20 else 2 if (cloud or 0) < 70 else 3
    return WMO.get(code, "")


def compass(deg: float | None) -> str:
    return "" if deg is None else POINTS[round(deg / 22.5) % 16]


def effects(w: dict | None) -> list[str]:
    """Plain-language notes for the kickoff reading. Only wind and cold are in the projections (backtested);
    the rest is shown as context and says so."""
    if not w or w.get("indoor"):
        return []
    out = []
    if w["wind"] >= 15:
        out.append(f"Wind of {w['wind']} mph. In past games this much wind cut passing about 15%, and our projections trim passing and receiving yards.")
    elif w["wind"] >= 8:
        out.append(f"Breezy ({w['wind']} mph). A small trim is applied to passing and receiving projections.")
    if w["temp"] < 40:
        out.append(f"Cold ({w['temp']}\u00b0F). Passing projections are trimmed slightly.")
    if (w.get("rain") or 0) >= 50 or (w.get("precip_in") or 0) >= 0.05:
        out.append("Wet conditions likely. This is not factored into projections: we found no reliable effect to measure.")
    if not out:
        out.append("No weather concerns. Nothing is adjusted in the projections.")
    return out


def impact(hours: list[dict]) -> dict:
    """How much this forecast changes passing, using the same backtested trims as the projections, averaged over the
    four hours shown. pct = average cut to passing and receiving yards. Rain and snow are context only (no reliable effect found)."""
    if not hours:
        return {"pct": 0, "level": "none", "drivers": []}
    f = sum(passing_factor({"wind": h["wind"], "temp": h["temp"], "indoor": False}) for h in hours) / len(hours)
    pct = round((1 - f) * 100)
    wind = max(h["wind"] for h in hours)
    cold = min(h["temp"] for h in hours)
    drivers = []
    if wind >= 8:
        drivers.append(f"wind up to {wind} mph")
    if cold < 40:
        drivers.append(f"cold, down to {cold}\u00b0F")
    wet = max((h.get("rain") or 0) for h in hours)
    if wet >= 50:
        drivers.append(f"{wet}% chance of precipitation (not scored)")
    level = "none" if pct <= 0 else "minor" if pct < 5 else "moderate" if pct < 12 else "strong"
    return {"pct": pct, "level": level, "drivers": drivers}


def report_many(games: list[dict]) -> dict:
    """games: [{"id","lat","lon","tip_utc","indoor"}] -> {id: {"indoor": bool, "hours": [...], "effects": [...]}} or None.
    Four hourly readings starting at kickoff. One request covers every outdoor game."""
    roof = lambda g: g.get("roof") or ("fixed" if g["indoor"] else "open")  # noqa: E731
    out = {g["id"]: ({"indoor": True, "roof": roof(g), "hours": [], "effects": [], "impact": {"pct": 0, "level": "none", "drivers": []}}
                     if roof(g) in ("fixed", "canopy") else None) for g in games}
    wet = [g for g in games if roof(g) in ("open", "retractable")]
    if not wet:
        return out
    fields = ("temperature_2m,apparent_temperature,relative_humidity_2m,precipitation_probability,precipitation,"
              "weather_code,wind_speed_10m,wind_gusts_10m,wind_direction_10m,cloud_cover")
    try:
        data = get_json(URL, params={
            "latitude": ",".join(str(g["lat"]) for g in wet), "longitude": ",".join(str(g["lon"]) for g in wet),
            "timezone": "UTC", "forecast_days": 14, "past_days": 1, "temperature_unit": "fahrenheit", "wind_speed_unit": "mph",
            "precipitation_unit": "inch", "hourly": fields}, retries=3, timeout=30)
        blocks = data if isinstance(data, list) else [data]
        for g, blk in zip(wet, blocks):
            h = blk.get("hourly") or {}
            times = h.get("time") or []
            if not times:
                continue
            tip = datetime.fromisoformat(g["tip_utc"]).astimezone(timezone.utc).replace(tzinfo=None)
            i0 = min(range(len(times)), key=lambda k: abs(datetime.fromisoformat(times[k]) - tip))
            at = lambda k, i: (h.get(k) or [None] * len(times))[i]  # noqa: E731
            hours = []
            for i in range(i0, min(i0 + 4, len(times))):
                if at("temperature_2m", i) is None or at("wind_speed_10m", i) is None:
                    continue
                r = lambda k, i=i, nd=0: (None if at(k, i) is None else round(at(k, i), nd) if nd else round(at(k, i)))  # noqa: E731
                hours.append({"utc": times[i] + "Z", "temp": r("temperature_2m"), "feels": r("apparent_temperature"),
                              "humidity": r("relative_humidity_2m"), "rain": r("precipitation_probability"),
                              "precip_in": r("precipitation", nd=2), "wind": r("wind_speed_10m"), "gust": r("wind_gusts_10m"),
                              "dir": r("wind_direction_10m"), "dir_txt": compass(at("wind_direction_10m", i)),
                              "cloud": r("cloud_cover"),
                              "cond": condition(at("weather_code", i), at("precipitation_probability", i), at("cloud_cover", i))})
            if hours:
                k = hours[0]
                rep = {"indoor": False, "roof": "open", "hours": hours, "effects": effects({**k, "indoor": False}), "impact": impact(hours)}
                if roof(g) == "retractable":
                    # Roof is decided by the home team close to kickoff and is not published ahead of time, so this game is never
                    # scored as bad weather and nothing is adjusted. The outdoor numbers are kept for context only.
                    rep["roof"] = "retractable"
                    rep["if_open"] = rep["impact"]
                    rep["impact"] = {"pct": 0, "level": "roof", "drivers": []}
                    rep["effects"] = ["Retractable roof. The home team decides whether to open it close to kickoff, and it is not announced ahead of time. "
                                      "These readings are what the weather is outside; nothing is adjusted in the projections."]
                out[g["id"]] = rep
    except (SourceError, ValueError, KeyError, TypeError) as e:
        log.warning("weather report unavailable: %s", e)
    return out
