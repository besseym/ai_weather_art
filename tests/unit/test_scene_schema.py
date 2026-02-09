import pytest
from pydantic import ValidationError

from weather_art.scene_schema import SceneResponse


VALID_SCENE = {
    "scene": {
        "canvas": {"width": 800, "height": 600},
        "background": {
            "type": "gradient",
            "colors": ["#1a1a2e", "#0f3460"],
            "direction": "vertical",
        },
        "elements": [
            {"type": "glow", "x": 650, "y": 100, "radius": 120, "color": "#FFD700", "intensity": 0.6},
            {"type": "ellipse", "x": 650, "y": 100, "width": 80, "height": 80, "fill": "#FFD700"},
            {"type": "ellipse", "x": 300, "y": 150, "width": 180, "height": 60, "fill": "#cccccc", "opacity": 0.7},
            {"type": "particle_system", "preset": "rain", "color": "#aaccff", "opacity": 0.6},
            {"type": "rect", "x": 0, "y": 500, "width": 800, "height": 100, "fill": "#2d4a2d"},
            {"type": "line", "x1": 400, "y1": 200, "x2": 420, "y2": 350, "stroke": "#ffffff", "stroke_weight": 3},
            {"type": "text", "content": "Rainy Day", "x": 10, "y": 30, "size": 20, "fill": "#ffffff"},
        ],
        "metadata": {"title": "Rainy Evening", "weather_summary": "Rain, 8C, wind 25km/h"},
    }
}


def test_valid_full_scene():
    response = SceneResponse.model_validate(VALID_SCENE)
    assert response.scene.canvas.width == 800
    assert response.scene.background.type == "gradient"
    assert len(response.scene.elements) == 7
    assert response.scene.metadata.title == "Rainy Evening"


def test_valid_minimal_scene():
    minimal = {"scene": {"elements": []}}
    response = SceneResponse.model_validate(minimal)
    assert response.scene.canvas.width == 800
    assert len(response.scene.elements) == 0


def test_solid_background():
    data = {"scene": {"background": {"type": "solid", "color": "#ff0000"}, "elements": []}}
    response = SceneResponse.model_validate(data)
    assert response.scene.background.type == "solid"
    assert response.scene.background.color == "#ff0000"


def test_all_element_types_parsed():
    response = SceneResponse.model_validate(VALID_SCENE)
    types = {e.type for e in response.scene.elements}
    assert types == {"glow", "ellipse", "particle_system", "rect", "line", "text"}


def test_ellipse_as_circle():
    """Ellipse with equal width/height replaces the old circle type."""
    data = {
        "scene": {
            "elements": [
                {"type": "ellipse", "x": 100, "y": 100, "width": 80, "height": 80, "fill": "#FFD700"}
            ]
        }
    }
    response = SceneResponse.model_validate(data)
    el = response.scene.elements[0]
    assert el.type == "ellipse"
    assert el.width == el.height == 80


def test_particle_system_preset_rain():
    data = {
        "scene": {
            "elements": [
                {"type": "particle_system", "preset": "rain", "color": "#aabbcc"}
            ]
        }
    }
    response = SceneResponse.model_validate(data)
    ps = response.scene.elements[0]
    assert ps.preset == "rain"
    assert ps.particle_shape == "line"
    assert ps.count == 200
    assert ps.speed == 5.0
    assert ps.angle == 260.0
    assert ps.color == "#aabbcc"


def test_particle_system_preset_snow():
    data = {
        "scene": {
            "elements": [
                {"type": "particle_system", "preset": "snow", "color": "#ffffff"}
            ]
        }
    }
    response = SceneResponse.model_validate(data)
    ps = response.scene.elements[0]
    assert ps.particle_shape == "circle"
    assert ps.speed == 1.5
    assert ps.drift == 1.5


def test_particle_system_preset_with_override():
    data = {
        "scene": {
            "elements": [
                {"type": "particle_system", "preset": "rain", "color": "#ff0000", "count": 50, "speed": 10.0}
            ]
        }
    }
    response = SceneResponse.model_validate(data)
    ps = response.scene.elements[0]
    assert ps.count == 50
    assert ps.speed == 10.0
    assert ps.angle == 260.0
    assert ps.particle_shape == "line"


def test_particle_system_preset_stars():
    data = {
        "scene": {
            "elements": [
                {"type": "particle_system", "preset": "stars", "color": "#ffffcc"}
            ]
        }
    }
    response = SceneResponse.model_validate(data)
    ps = response.scene.elements[0]
    assert ps.speed == 0.0
    assert ps.particle_shape == "circle"


def test_particle_count_too_high():
    data = {
        "scene": {
            "elements": [
                {"type": "particle_system", "preset": "rain", "color": "#fff", "count": 5000}
            ]
        }
    }
    with pytest.raises(ValidationError):
        SceneResponse.model_validate(data)


def test_missing_scene_key():
    with pytest.raises(ValidationError):
        SceneResponse.model_validate({"not_scene": {}})


def test_invalid_element_type():
    data = {"scene": {"elements": [{"type": "hexagon", "x": 0, "y": 0}]}}
    with pytest.raises(ValidationError):
        SceneResponse.model_validate(data)


def test_removed_types_rejected():
    """circle, triangle, arc are no longer valid element types."""
    for removed_type in ["circle", "triangle", "arc"]:
        data = {"scene": {"elements": [{"type": removed_type, "x": 0, "y": 0}]}}
        with pytest.raises(ValidationError):
            SceneResponse.model_validate(data)


def test_gradient_needs_at_least_two_colors():
    data = {"scene": {"background": {"type": "gradient", "colors": ["#000"]}, "elements": []}}
    with pytest.raises(ValidationError):
        SceneResponse.model_validate(data)