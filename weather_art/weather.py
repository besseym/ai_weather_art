import requests

from weather_art.config import OPEN_METEO_FORECAST_URL

WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

CURRENT_PARAMS = (
    "temperature_2m,relative_humidity_2m,apparent_temperature,"
    "weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,"
    "wind_gusts_10m,precipitation,rain,snowfall,is_day"
)


def get_current_weather(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo for the given coordinates.

    Returns a clean dict with human-readable keys.
    """
    response = requests.get(
        OPEN_METEO_FORECAST_URL,
        params={"latitude": lat, "longitude": lon, "current": CURRENT_PARAMS},
        timeout=10,
    )
    response.raise_for_status()
    current = response.json()["current"]

    weather_code = current["weather_code"]
    return {
        "temperature_c": current["temperature_2m"],
        "apparent_temperature_c": current["apparent_temperature"],
        "humidity_pct": current["relative_humidity_2m"],
        "weather_code": weather_code,
        "weather_description": WMO_CODES.get(weather_code, "Unknown"),
        "cloud_cover_pct": current["cloud_cover"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "wind_direction_deg": current["wind_direction_10m"],
        "wind_gusts_kmh": current["wind_gusts_10m"],
        "precipitation_mm": current["precipitation"],
        "rain_mm": current["rain"],
        "snowfall_cm": current["snowfall"],
        "is_day": bool(current["is_day"]),
    }