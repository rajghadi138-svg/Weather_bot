"""
weather_api.py — Open-Meteo helpers (free, no API key required)
  • geocode(city)        → {name, country, lat, lon}
  • fetch_weather(lat,lon) → current + daily forecast dict
  • describe(code)       → human text for a WMO weather code
  • fmt_time / WMO maps
"""

import datetime as dt
from zoneinfo import ZoneInfo

GEO_URL  = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes → short description
WMO = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Dense drizzle",
    56: "Freezing drizzle", 57: "Freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Violent showers",
    85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm w/ hail", 99: "Severe thunderstorm",
}

def describe(code: int) -> str:
    return WMO.get(code, "Unknown")


async def geocode(session, city: str):
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    async with session.get(GEO_URL, params=params) as r:
        if r.status != 200:
            return None
        data = await r.json()
    results = data.get("results")
    if not results:
        return None
    top = results[0]
    return {
        "name": top["name"],
        "country": top.get("country_code", top.get("country", "")),
        "lat": top["latitude"],
        "lon": top["longitude"],
    }


async def fetch_weather(session, lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "weather_code", "wind_speed_10m",
        ]),
        "daily": ",".join([
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "sunrise", "sunset", "precipitation_probability_max",
        ]),
        "timezone": "auto",
        "forecast_days": 1,
        "wind_speed_unit": "kmh",
    }
    async with session.get(FORECAST, params=params) as r:
        r.raise_for_status()
        return await r.json()


def fmt_time(iso: str) -> str:
    """'2026-06-24T05:51' → '05:51'."""
    try:
        return dt.datetime.fromisoformat(iso).strftime("%H:%M")
    except ValueError:
        return iso
