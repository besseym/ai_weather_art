from unittest.mock import patch, Mock

from weather_art.weather import get_current_weather, WMO_CODES


BERLIN_WEATHER_RESPONSE = {
    "current": {
        "temperature_2m": 8.3,
        "apparent_temperature": 5.1,
        "relative_humidity_2m": 72,
        "weather_code": 61,
        "cloud_cover": 85,
        "wind_speed_10m": 15.2,
        "wind_direction_10m": 230,
        "wind_gusts_10m": 28.4,
        "precipitation": 1.2,
        "rain": 1.2,
        "snowfall": 0.0,
        "is_day": 1,
    }
}


@patch("weather_art.weather.requests.get")
def test_get_current_weather_success(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = BERLIN_WEATHER_RESPONSE
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    result = get_current_weather(52.52, 13.41)

    assert result["temperature_c"] == 8.3
    assert result["apparent_temperature_c"] == 5.1
    assert result["humidity_pct"] == 72
    assert result["weather_code"] == 61
    assert result["weather_description"] == "Slight rain"
    assert result["cloud_cover_pct"] == 85
    assert result["wind_speed_kmh"] == 15.2
    assert result["wind_direction_deg"] == 230
    assert result["wind_gusts_kmh"] == 28.4
    assert result["precipitation_mm"] == 1.2
    assert result["rain_mm"] == 1.2
    assert result["snowfall_cm"] == 0.0
    assert result["is_day"] is True
    mock_get.assert_called_once()


@patch("weather_art.weather.requests.get")
def test_get_current_weather_night(mock_get):
    night_data = {
        "current": {**BERLIN_WEATHER_RESPONSE["current"], "is_day": 0}
    }
    mock_resp = Mock()
    mock_resp.json.return_value = night_data
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    result = get_current_weather(52.52, 13.41)
    assert result["is_day"] is False


@patch("weather_art.weather.requests.get")
def test_get_current_weather_unknown_code(mock_get):
    unknown_data = {
        "current": {**BERLIN_WEATHER_RESPONSE["current"], "weather_code": 999}
    }
    mock_resp = Mock()
    mock_resp.json.return_value = unknown_data
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    result = get_current_weather(52.52, 13.41)
    assert result["weather_description"] == "Unknown"


def test_wmo_codes_coverage():
    """Verify key WMO codes are present."""
    assert 0 in WMO_CODES  # Clear sky
    assert 95 in WMO_CODES  # Thunderstorm
    assert 75 in WMO_CODES  # Heavy snowfall