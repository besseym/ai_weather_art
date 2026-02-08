import requests

from weather_art.config import OPEN_METEO_GEOCODING_URL


def geocode_city(city_name: str) -> dict:
    """Look up a city via Open-Meteo Geocoding API.

    Returns dict with keys: name, latitude, longitude, country, timezone.
    Raises ValueError if the city is not found.
    """
    response = requests.get(
        OPEN_METEO_GEOCODING_URL,
        params={"name": city_name, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"City not found: {city_name}")

    result = data["results"][0]
    return {
        "name": result["name"],
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "country": result.get("country", ""),
        "timezone": result.get("timezone", ""),
    }