from unittest.mock import patch, Mock

import pytest

from weather_art.geocoding import geocode_city


BERLIN_RESPONSE = {
    "results": [
        {
            "name": "Berlin",
            "latitude": 52.52437,
            "longitude": 13.41053,
            "country": "Germany",
            "timezone": "Europe/Berlin",
        }
    ]
}


@patch("weather_art.geocoding.requests.get")
def test_geocode_city_success(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = BERLIN_RESPONSE
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    result = geocode_city("Berlin")

    assert result["name"] == "Berlin"
    assert result["latitude"] == 52.52437
    assert result["longitude"] == 13.41053
    assert result["country"] == "Germany"
    assert result["timezone"] == "Europe/Berlin"
    mock_get.assert_called_once()


@patch("weather_art.geocoding.requests.get")
def test_geocode_city_not_found(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {}
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    with pytest.raises(ValueError, match="City not found"):
        geocode_city("Nonexistentcity12345")


@patch("weather_art.geocoding.requests.get")
def test_geocode_city_empty_results(mock_get):
    mock_resp = Mock()
    mock_resp.json.return_value = {"results": []}
    mock_resp.raise_for_status = Mock()
    mock_get.return_value = mock_resp

    with pytest.raises(ValueError, match="City not found"):
        geocode_city("Nonexistentcity12345")