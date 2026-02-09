import pytest

from weather_art.weather_agent import describe_weather

pytestmark = pytest.mark.integration


def test_describe_weather_by_city():
    result = describe_weather("Describe the current weather in Berlin.")
    assert isinstance(result, str)
    assert len(result) > 20


def test_describe_weather_with_coords():
    result = describe_weather(
        "Describe the current weather at latitude 52.52, longitude 13.41."
    )
    assert isinstance(result, str)
    assert len(result) > 20