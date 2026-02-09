import pytest

from weather_art.geocoding import geocode_city

pytestmark = pytest.mark.integration


def test_geocode_known_city():
    result = geocode_city("Berlin")
    assert result["name"] == "Berlin"
    assert result["country"] == "Germany"
    assert abs(result["latitude"] - 52.52) < 0.5
    assert abs(result["longitude"] - 13.41) < 0.5
    assert result["timezone"] != ""


def test_geocode_city_not_found():
    with pytest.raises(ValueError, match="City not found"):
        geocode_city("Zzxxqqnonexistent")