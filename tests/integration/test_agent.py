import pytest

from weather_art.agent import generate_scene
from weather_art.scene_schema import SceneResponse

pytestmark = pytest.mark.integration


def test_generate_scene_with_city():
    """End-to-end: city name -> agent -> validated scene JSON."""
    result = generate_scene("Berlin")

    validated = SceneResponse.model_validate(result)
    scene = validated.scene

    assert scene.canvas.width == 800
    assert scene.canvas.height == 600
    assert len(scene.elements) > 0
    assert scene.metadata.title != ""


def test_generate_scene_with_coords():
    """End-to-end: coordinates -> agent -> validated scene JSON."""
    result = generate_scene("Berlin", latitude=52.52, longitude=13.41)

    validated = SceneResponse.model_validate(result)
    scene = validated.scene

    assert len(scene.elements) > 0


def test_generate_scene_with_style_prompt():
    """End-to-end: city + style prompt -> agent -> validated scene JSON."""
    result = generate_scene("Tokyo", style_prompt="watercolor")

    validated = SceneResponse.model_validate(result)
    scene = validated.scene

    assert len(scene.elements) > 0
    assert scene.metadata.weather_summary != ""