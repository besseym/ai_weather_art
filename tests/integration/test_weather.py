import pytest

from weather_art.weather import get_current_weather, WMO_CODES

pytestmark = pytest.mark.integration

# Berlin coordinates
BERLIN_LAT = 52.52
BERLIN_LON = 13.41


def test_get_current_weather_returns_all_keys():
    result = get_current_weather(BERLIN_LAT, BERLIN_LON)
    expected_keys = {
        "temperature_c",
        "apparent_temperature_c",
        "humidity_pct",
        "weather_code",
        "weather_description",
        "cloud_cover_pct",
        "wind_speed_kmh",
        "wind_direction_deg",
        "wind_gusts_kmh",
        "precipitation_mm",
        "rain_mm",
        "snowfall_cm",
        "is_day",
    }
    assert set(result.keys()) == expected_keys


def test_get_current_weather_value_ranges():
    result = get_current_weather(BERLIN_LAT, BERLIN_LON)
    assert -60 <= result["temperature_c"] <= 60
    assert 0 <= result["humidity_pct"] <= 100
    assert 0 <= result["cloud_cover_pct"] <= 100
    assert 0 <= result["wind_speed_kmh"]
    assert 0 <= result["wind_direction_deg"] <= 360
    assert result["precipitation_mm"] >= 0
    assert isinstance(result["is_day"], bool)
    assert result["weather_code"] in WMO_CODES