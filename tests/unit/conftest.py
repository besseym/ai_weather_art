import pytest

from app import app as flask_app


SAMPLE_SCENE = {
    "scene": {
        "canvas": {"width": 800, "height": 600},
        "background": {"type": "gradient", "colors": ["#1a1a2e", "#0f3460"], "direction": "vertical"},
        "elements": [
            {"type": "glow", "x": 650, "y": 100, "radius": 120, "color": "#FFD700", "intensity": 0.6},
            {"type": "ellipse", "x": 650, "y": 100, "width": 80, "height": 80, "fill": "#FFD700"},
            {
                "type": "particle_system",
                "preset": "rain",
                "color": "#aaccee",
                "opacity": 0.6,
            },
        ],
        "metadata": {"title": "Rainy Evening", "weather_summary": "Rain, 8C, wind 25km/h"},
    }
}

SAMPLE_GEOCODE_RESULT = {
    "name": "Berlin",
    "latitude": 52.52,
    "longitude": 13.41,
    "country": "Germany",
    "timezone": "Europe/Berlin",
}

SAMPLE_WEATHER_DATA = {
    "temperature_c": 8.0,
    "humidity_pct": 85,
    "apparent_temperature_c": 5.2,
    "weather_code": 61,
    "weather_description": "Slight rain",
    "cloud_cover_pct": 90,
    "wind_speed_kmh": 25.0,
    "wind_direction_deg": 220,
    "wind_gusts_kmh": 40.0,
    "precipitation_mm": 1.2,
    "rain_mm": 1.2,
    "snowfall_cm": 0.0,
    "is_day": False,
}


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def sample_scene():
    return SAMPLE_SCENE


@pytest.fixture
def sample_geocode():
    return SAMPLE_GEOCODE_RESULT


@pytest.fixture
def sample_weather():
    return SAMPLE_WEATHER_DATA