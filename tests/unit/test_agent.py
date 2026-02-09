import json
from unittest.mock import patch, Mock, MagicMock

import pytest

from weather_art.agent import (
    extract_json_from_response,
    generate_scene,
    get_scene_format,
    validate_scene,
)


VALID_SCENE_JSON = json.dumps({
    "scene": {
        "canvas": {"width": 800, "height": 600},
        "background": {"type": "solid", "color": "#87CEEB"},
        "layers": [
            {
                "id": "sky",
                "opacity": 1.0,
                "elements": [
                    {"type": "glow", "x": 650, "y": 100, "radius": 120, "color": "#FFD700", "intensity": 0.6},
                    {"type": "circle", "x": 650, "y": 100, "radius": 40, "fill": "#FFD700"},
                ],
            }
        ],
        "metadata": {"title": "Sunny Day", "weather_summary": "Clear, 22C"},
    }
})


class TestExtractJson:
    def test_plain_json(self):
        result = extract_json_from_response('{"scene": {}}')
        assert result == {"scene": {}}

    def test_json_with_markdown_fences(self):
        text = '```json\n{"scene": {}}\n```'
        result = extract_json_from_response(text)
        assert result == {"scene": {}}

    def test_json_with_bare_fences(self):
        text = '```\n{"scene": {}}\n```'
        result = extract_json_from_response(text)
        assert result == {"scene": {}}

    def test_json_with_surrounding_whitespace(self):
        text = '  \n  {"scene": {}}  \n  '
        result = extract_json_from_response(text)
        assert result == {"scene": {}}

    def test_invalid_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            extract_json_from_response("not json at all")


class TestGetSceneFormat:
    def test_returns_schema_reference(self):
        result = get_scene_format()
        assert result["status"] == "success"
        text = result["content"][0]["text"]
        assert "particle_system" in text
        assert "glow" in text
        assert "circle" in text
        assert "Weather-to-Visual" in text


class TestGenerateScene:
    @patch("weather_art.agent.OllamaModel")
    @patch("weather_art.agent.Agent")
    def test_generate_scene_with_city(self, MockAgent, MockModel):
        mock_agent_instance = MagicMock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=VALID_SCENE_JSON)
        mock_agent_instance.return_value = mock_result
        MockAgent.return_value = mock_agent_instance

        scene = generate_scene("Berlin")

        assert scene["scene"]["metadata"]["title"] == "Sunny Day"
        mock_agent_instance.assert_called_once()
        call_args = mock_agent_instance.call_args[0][0]
        assert "Berlin" in call_args

    @patch("weather_art.agent.OllamaModel")
    @patch("weather_art.agent.Agent")
    def test_generate_scene_with_coords(self, MockAgent, MockModel):
        mock_agent_instance = MagicMock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=VALID_SCENE_JSON)
        mock_agent_instance.return_value = mock_result
        MockAgent.return_value = mock_agent_instance

        scene = generate_scene("Berlin", latitude=52.52, longitude=13.41)

        call_args = mock_agent_instance.call_args[0][0]
        assert "52.52" in call_args
        assert "13.41" in call_args

    @patch("weather_art.agent.OllamaModel")
    @patch("weather_art.agent.Agent")
    def test_generate_scene_with_style(self, MockAgent, MockModel):
        mock_agent_instance = MagicMock()
        mock_result = Mock()
        mock_result.__str__ = Mock(return_value=VALID_SCENE_JSON)
        mock_agent_instance.return_value = mock_result
        MockAgent.return_value = mock_agent_instance

        generate_scene("Berlin", style_prompt="watercolor")

        call_args = mock_agent_instance.call_args[0][0]
        assert "watercolor" in call_args

class TestValidateScene:
    def test_validate_scene_success(self):
        result = validate_scene(VALID_SCENE_JSON)
        assert result["status"] == "success"
        parsed = json.loads(result["content"][0]["text"])
        assert parsed["scene"]["metadata"]["title"] == "Sunny Day"

    def test_validate_scene_invalid_json(self):
        result = validate_scene("not json at all")
        assert result["status"] == "error"
        assert "Validation failed" in result["content"][0]["text"]

    def test_validate_scene_bad_schema(self):
        result = validate_scene('{"scene": {"layers": [{"id": "x", "elements": [{"type": "bogus"}]}]}}')
        assert result["status"] == "error"
        assert "Validation failed" in result["content"][0]["text"]

    def test_validate_scene_strips_fences(self):
        fenced = f"```json\n{VALID_SCENE_JSON}\n```"
        result = validate_scene(fenced)
        assert result["status"] == "success"