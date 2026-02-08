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
        "layers": [
            {
                "id": "sky",
                "opacity": 1.0,
                "elements": [
                    {
                        "type": "glow",
                        "x": 650,
                        "y": 100,
                        "radius": 120,
                        "color": "#FFD700",
                        "intensity": 0.6,
                    },
                    {
                        "type": "circle",
                        "x": 650,
                        "y": 100,
                        "radius": 40,
                        "fill": "#FFD700",
                        "opacity": 1.0,
                    },
                    {
                        "type": "ellipse",
                        "x": 300,
                        "y": 150,
                        "width": 180,
                        "height": 60,
                        "fill": "#cccccc",
                        "opacity": 0.7,
                    },
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
                        "speed": 4.0,
                        "angle": 260,
                        "drift": 0.5,
                        "size": 5,
                        "color": "#aaccff",
                        "opacity": 0.6,
                    }
                ],
            },
            {
                "id": "ground",
                "elements": [
                    {
                        "type": "rect",
                        "x": 0,
                        "y": 500,
                        "width": 800,
                        "height": 100,
                        "fill": "#2d4a2d",
                    },
                    {
                        "type": "triangle",
                        "x1": 100,
                        "y1": 500,
                        "x2": 150,
                        "y2": 400,
                        "x3": 200,
                        "y3": 500,
                        "fill": "#1a3a1a",
                    },
                    {
                        "type": "line",
                        "x1": 400,
                        "y1": 200,
                        "x2": 420,
                        "y2": 350,
                        "stroke": "#ffffff",
                        "stroke_weight": 3,
                    },
                    {
                        "type": "arc",
                        "x": 400,
                        "y": 300,
                        "width": 200,
                        "height": 100,
                        "start_angle": 3.14,
                        "stop_angle": 6.28,
                        "stroke": "#ff0000",
                    },
                    {
                        "type": "text",
                        "content": "Rainy Day",
                        "x": 10,
                        "y": 30,
                        "size": 20,
                        "fill": "#ffffff",
                    },
                ],
            },
        ],
        "metadata": {
            "title": "Rainy Evening",
            "weather_summary": "Rain, 8C, wind 25km/h",
        },
    }
}


def test_valid_full_scene():
    response = SceneResponse.model_validate(VALID_SCENE)
    assert response.scene.canvas.width == 800
    assert response.scene.background.type == "gradient"
    assert len(response.scene.layers) == 3
    assert response.scene.metadata.title == "Rainy Evening"


def test_valid_minimal_scene():
    minimal = {"scene": {"layers": []}}
    response = SceneResponse.model_validate(minimal)
    assert response.scene.canvas.width == 800
    assert response.scene.canvas.height == 600
    assert len(response.scene.layers) == 0


def test_solid_background():
    data = {
        "scene": {
            "background": {"type": "solid", "color": "#000000"},
            "layers": [],
        }
    }
    response = SceneResponse.model_validate(data)
    assert response.scene.background.type == "solid"
    assert response.scene.background.color == "#000000"


def test_all_element_types_parsed():
    response = SceneResponse.model_validate(VALID_SCENE)
    all_elements = []
    for layer in response.scene.layers:
        all_elements.extend(layer.elements)
    types = {e.type for e in all_elements}
    assert types == {"glow", "circle", "ellipse", "particle_system", "rect", "triangle", "line", "arc", "text"}


def test_particle_system_defaults():
    data = {
        "scene": {
            "layers": [
                {
                    "id": "rain",
                    "elements": [{"type": "particle_system"}],
                }
            ]
        }
    }
    response = SceneResponse.model_validate(data)
    ps = response.scene.layers[0].elements[0]
    assert ps.count == 100
    assert ps.speed == 2.0
    assert ps.particle_shape == "circle"


def test_particle_count_too_high():
    data = {
        "scene": {
            "layers": [
                {
                    "id": "rain",
                    "elements": [{"type": "particle_system", "count": 5000}],
                }
            ]
        }
    }
    with pytest.raises(ValidationError):
        SceneResponse.model_validate(data)


def test_missing_scene_key():
    with pytest.raises(ValidationError):
        SceneResponse.model_validate({"not_scene": {}})


def test_invalid_element_type():
    data = {
        "scene": {
            "layers": [
                {
                    "id": "bad",
                    "elements": [{"type": "hexagon", "x": 0, "y": 0}],
                }
            ]
        }
    }
    with pytest.raises(ValidationError):
        SceneResponse.model_validate(data)


def test_gradient_needs_at_least_two_colors():
    data = {
        "scene": {
            "background": {"type": "gradient", "colors": ["#000"]},
            "layers": [],
        }
    }
    with pytest.raises(ValidationError):
        SceneResponse.model_validate(data)