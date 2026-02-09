import json
from unittest.mock import patch

from tests.unit.conftest import SAMPLE_SCENE, SAMPLE_GEOCODE_RESULT


class TestIndex:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"AI Weather Art" in resp.data


class TestApiGenerate:
    @patch("weather_art.routes.generate_scene")
    def test_generate_success(self, mock_gen, client):
        mock_gen.return_value = SAMPLE_SCENE
        resp = client.post(
            "/api/generate",
            json={"location": "Berlin"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["scene"]["metadata"]["title"] == "Rainy Evening"
        mock_gen.assert_called_once_with(
            location="Berlin", latitude=None, longitude=None, style_prompt=""
        )

    @patch("weather_art.routes.generate_scene")
    def test_generate_with_coords(self, mock_gen, client):
        mock_gen.return_value = SAMPLE_SCENE
        resp = client.post(
            "/api/generate",
            json={"location": "Berlin", "latitude": 52.52, "longitude": 13.41},
        )
        assert resp.status_code == 200
        mock_gen.assert_called_once_with(
            location="Berlin", latitude=52.52, longitude=13.41, style_prompt=""
        )

    @patch("weather_art.routes.generate_scene")
    def test_generate_with_style(self, mock_gen, client):
        mock_gen.return_value = SAMPLE_SCENE
        resp = client.post(
            "/api/generate",
            json={"location": "Berlin", "style_prompt": "watercolor"},
        )
        assert resp.status_code == 200
        mock_gen.assert_called_once_with(
            location="Berlin", latitude=None, longitude=None, style_prompt="watercolor"
        )

    def test_generate_missing_body(self, client):
        resp = client.post("/api/generate", content_type="application/json")
        assert resp.status_code == 400

    def test_generate_missing_location(self, client):
        resp = client.post("/api/generate", json={})
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    @patch("weather_art.routes.generate_scene")
    def test_generate_agent_error(self, mock_gen, client):
        mock_gen.side_effect = RuntimeError("Ollama unavailable")
        resp = client.post("/api/generate", json={"location": "Berlin"})
        assert resp.status_code == 500
        assert "Ollama unavailable" in resp.get_json()["error"]


class TestApiGeocode:
    @patch("weather_art.routes.geocode_city")
    def test_geocode_success(self, mock_geo, client):
        mock_geo.return_value = SAMPLE_GEOCODE_RESULT
        resp = client.get("/api/geocode?city=Berlin")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["name"] == "Berlin"
        assert data["latitude"] == 52.52

    def test_geocode_missing_param(self, client):
        resp = client.get("/api/geocode")
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    @patch("weather_art.routes.geocode_city")
    def test_geocode_not_found(self, mock_geo, client):
        mock_geo.side_effect = ValueError("City not found: Xyzzy")
        resp = client.get("/api/geocode?city=Xyzzy")
        assert resp.status_code == 404
        assert "City not found" in resp.get_json()["error"]