import pytest

from app import app as flask_app


SAMPLE_SCENE = {
    "scene": {
        "canvas": {"width": 800, "height": 600},
        "background": {"type": "gradient", "colors": ["#1a1a2e", "#0f3460"], "direction": "vertical"},
        "layers": [
            {
                "id": "sky",
                "opacity": 1.0,
                "elements": [
                    {"type": "glow", "x": 650, "y": 100, "radius": 120, "color": "#FFD700", "intensity": 0.6},
                    {"type": "circle", "x": 650, "y": 100, "radius": 40, "fill": "#FFD700"},
                ],
            },
            {
                "id": "weather",
                "opacity": 0.8,
                "elements": [
                    {
                        "type": "particle_system",
                        "particle_shape": "line",
                        "count": 200,
                        "region": {"x": 0, "y": 0, "width": 800, "height": 600},
                        "speed": 5.0,
                        "angle": 260,
                        "size": 4,
                        "color": "#aaccee",
                        "opacity": 0.6,
                    }
                ],
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