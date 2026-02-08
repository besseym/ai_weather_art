from flask import Blueprint, jsonify, render_template, request

from weather_art.agent import generate_scene
from weather_art.geocoding import geocode_city

bp = Blueprint("weather_art", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    location = data.get("location", "").strip()
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    style_prompt = data.get("style_prompt", "")

    if not location and (latitude is None or longitude is None):
        return jsonify({"error": "Provide a location name or latitude/longitude"}), 400

    try:
        scene = generate_scene(
            location=location or "Unknown",
            latitude=latitude,
            longitude=longitude,
            style_prompt=style_prompt,
        )
        return jsonify(scene)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/api/geocode")
def api_geocode():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Missing 'city' query parameter"}), 400

    try:
        result = geocode_city(city)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500