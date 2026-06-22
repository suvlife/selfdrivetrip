"""Weather service - fetches weather data from wttr.in (free, no key needed) and OpenWeatherMap."""

import logging
from typing import Optional, Dict, Any, List

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def get_weather_from_wttr(city: str) -> Optional[Dict[str, Any]]:
    """Fetch weather from wttr.in (free, no API key needed)."""
    try:
        url = f"https://wttr.in/{city}?format=j1"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        current = data.get("current_condition", [{}])[0]
        forecasts = []

        for day in data.get("weather", [])[:7]:
            forecasts.append({
                "date": day.get("date", ""),
                "temperature_high": float(day.get("maxtempC", 0)),
                "temperature_low": float(day.get("mintempC", 0)),
                "weather_condition": day.get("hourly", [{}])[0].get("weatherDesc", [{}])[0].get("value", ""),
                "icon": day.get("hourly", [{}])[0].get("weatherCode", ""),
                "humidity": float(day.get("hourly", [{}])[0].get("humidity", "0")),
                "wind_speed": float(day.get("hourly", [{}])[0].get("windspeedKmph", "0")),
            })

        return {
            "city": city,
            "current": {
                "temperature": current.get("temp_C", ""),
                "humidity": current.get("humidity", ""),
                "wind_speed": current.get("windspeedKmph", ""),
                "weather_desc": current.get("weatherDesc", [{}])[0].get("value", ""),
                "feels_like": current.get("FeelsLikeC", ""),
            },
            "forecasts": forecasts,
        }
    except Exception as e:
        logger.error(f"wttr.in API error for {city}: {e}")
        return None


async def get_weather_from_owm(city: str) -> Optional[Dict[str, Any]]:
    """Fetch weather from OpenWeatherMap API."""
    api_key = settings.OPENWEATHERMAP_API_KEY
    if not api_key:
        return None

    try:
        # First geocode the city
        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
        async with httpx.AsyncClient(timeout=10.0) as client:
            geo_resp = await client.get(
                geo_url,
                params={"q": city, "limit": 1, "appid": api_key},
            )
            geo_resp.raise_for_status()
            geo_data = geo_resp.json()

        if not geo_data:
            return None

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        # Get 5-day forecast
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        async with httpx.AsyncClient(timeout=10.0) as client:
            forecast_resp = await client.get(
                forecast_url,
                params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
            )
            forecast_resp.raise_for_status()
            forecast_data = forecast_resp.json()

        # Process forecast
        forecasts = []
        seen_dates = set()
        for item in forecast_data.get("list", []):
            date = item.get("dt_txt", "").split(" ")[0]
            if date not in seen_dates and len(seen_dates) < 7:
                seen_dates.add(date)
                forecasts.append({
                    "date": date,
                    "temperature_high": float(item["main"].get("temp_max", 0)),
                    "temperature_low": float(item["main"].get("temp_min", 0)),
                    "weather_condition": item["weather"][0].get("description", ""),
                    "icon": item["weather"][0].get("icon", ""),
                    "humidity": float(item["main"].get("humidity", 0)),
                    "wind_speed": float(item["wind"].get("speed", 0)),
                })

        return {
            "city": city,
            "current": {
                "temperature": forecasts[0]["temperature_high"] if forecasts else "",
            },
            "forecasts": forecasts,
        }
    except Exception as e:
        logger.error(f"OpenWeatherMap API error for {city}: {e}")
        return None


async def get_weather(city: str) -> Dict[str, Any]:
    """Get weather data for a city. Tries OpenWeatherMap first, falls back to wttr.in."""
    # Try OWM first
    if settings.OPENWEATHERMAP_API_KEY:
        result = await get_weather_from_owm(city)
        if result:
            return result

    # Fallback to wttr.in
    result = await get_weather_from_wttr(city)
    if result:
        return result

    # Ultimate fallback
    return {
        "city": city,
        "current": {"temperature": "", "humidity": "", "wind_speed": "", "weather_desc": ""},
        "forecasts": [],
        "error": "Weather data unavailable",
    }
