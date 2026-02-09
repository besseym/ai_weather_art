import json
import re

from strands import Agent, tool
from strands.models import OllamaModel

from weather_art.config import OLLAMA_HOST, OLLAMA_MODEL_ID
from weather_art.geocoding import geocode_city
from weather_art.weather import get_current_weather
from weather_art.scene_schema import SceneResponse


@tool
def geocode_location(city_name: str) -> dict:
    """Look up geographic coordinates for a city name.

    Args:
        city_name: The name of the city to geocode (e.g. "Berlin", "Tokyo").

    Returns:
        Dictionary with name, latitude, longitude, country, and timezone.
    """
    result = geocode_city(city_name)
    return {"status": "success", "content": [{"text": json.dumps(result)}]}


@tool
def get_weather(latitude: float, longitude: float) -> dict:
    """Get current weather conditions for geographic coordinates.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.

    Returns:
        Dictionary with temperature, humidity, weather description, wind, precipitation, etc.
    """
    result = get_current_weather(latitude, longitude)
    return {"status": "success", "content": [{"text": json.dumps(result)}]}


@tool
def get_scene_format() -> dict:
    """Get the scene JSON format, element types, and artistic guidelines.

    Call this tool BEFORE generating your scene JSON to learn the exact schema,
    all available element types, weather-to-visual mappings, and color guidelines.

    Returns:
        Complete reference for the scene JSON format the renderer expects.
    """
    schema_ref = json.dumps(SceneResponse.model_json_schema(), indent=2)

    guide = f"""\
## Scene JSON Schema (auto-generated from Pydantic models)

{schema_ref}

## Structure Overview

Return a JSON object with this top-level shape:
{{
  "scene": {{
    "canvas": {{"width": 800, "height": 600}},
    "background": <background>,
    "layers": [<layer>, ...],
    "metadata": {{"title": "<short title>", "weather_summary": "<conditions summary>"}}
  }}
}}

### Background (pick one)
- Solid: {{"type": "solid", "color": "#hex"}}
- Gradient: {{"type": "gradient", "colors": ["#hex1", "#hex2"], "direction": "vertical"|"horizontal"}}

### Layers
Each layer: {{"id": "<name>", "opacity": 0.0-1.0, "elements": [<element>, ...]}}
Use 2-4 layers to organize the scene (e.g. sky, weather_effects, ground, foreground).

### 9 Element Types

1. circle — Sun, moon, dots
   {{"type": "circle", "x": N, "y": N, "radius": N, "fill": "#hex", "stroke": "#hex", "opacity": 0-1}}

2. ellipse — Clouds, puddles
   {{"type": "ellipse", "x": N, "y": N, "width": N, "height": N, "fill": "#hex", "opacity": 0-1}}

3. rect — Ground, buildings, sky bands
   {{"type": "rect", "x": N, "y": N, "width": N, "height": N, "fill": "#hex", "corner_radius": N, "opacity": 0-1}}

4. line — Lightning bolts, streaks
   {{"type": "line", "x1": N, "y1": N, "x2": N, "y2": N, "stroke": "#hex", "stroke_weight": N, "opacity": 0-1}}

5. triangle — Mountains, trees, rooftops
   {{"type": "triangle", "x1": N, "y1": N, "x2": N, "y2": N, "x3": N, "y3": N, "fill": "#hex", "opacity": 0-1}}

6. arc — Rainbows, curved shapes
   {{"type": "arc", "x": N, "y": N, "width": N, "height": N, "start_angle": radians, "stop_angle": radians, "stroke": "#hex", "opacity": 0-1}}

7. text — Labels, temperature display
   {{"type": "text", "content": "string", "x": N, "y": N, "size": N, "fill": "#hex", "opacity": 0-1}}

8. particle_system — Rain, snow, fog, dust (ANIMATED — the renderer handles movement)
   {{"type": "particle_system", "particle_shape": "circle"|"line"|"rect", "count": 1-1000, \
"region": {{"x": N, "y": N, "width": N, "height": N}}, "speed": N, "angle": degrees, \
"drift": N, "size": N, "color": "#hex", "opacity": 0-1}}

9. glow — Sun glow, moon halo, light sources
   {{"type": "glow", "x": N, "y": N, "radius": N, "color": "#hex", "intensity": 0-1}}

## Weather-to-Visual Mapping Guide

- Clear day: bright gradient (#87CEEB to #4682B4), sun circle + glow, maybe a few clouds
- Clear night: dark gradient (#0a0a2e to #1a1a3e), moon circle + glow, star circles
- Rain: grey gradient, dark clouds (ellipses), particle_system with shape "line", angle ~260, speed 4-6
- Snow: blue-grey gradient, particle_system with shape "circle", angle ~270, speed 1-2, drift 1-2
- Fog: muted gradient, particle_system with shape "circle", large size, low speed, high count, low opacity
- Thunderstorm: very dark gradient, line elements for lightning, rain particles, dark clouds
- Cloudy: grey gradient, multiple cloud ellipses at various positions and opacities
- Windy: use drift on particles, angled elements suggesting motion

## Color Guidelines
- Use hex colors only (e.g. "#FF6B35")
- Daytime: warm, bright palettes
- Nighttime: cool, dark palettes with accent colors for moon/stars
- Match mood to weather: cheerful yellows for sun, moody blues for rain, crisp whites for snow

## Rules
- Canvas is always 800x600
- All coordinates must be within the canvas bounds
- Use particle_system for any weather precipitation or atmospheric effects
- Include at least one glow element for sun or moon
- Keep total element count reasonable (under 30 elements across all layers)
"""
    return {"status": "success", "content": [{"text": guide}]}


@tool
def validate_scene(scene_json: str) -> dict:
    """Validate a scene JSON string against the schema.

    Call this tool with your generated scene JSON to check it is valid before
    returning it as your final answer. If validation fails, the error message
    will tell you what to fix.

    Args:
        scene_json: The complete scene JSON string to validate.

    Returns:
        Validation result: success with the validated JSON, or error with details.
    """
    try:
        raw = extract_json_from_response(scene_json)
        validated = SceneResponse.model_validate(raw)
        return {
            "status": "success",
            "content": [{"text": json.dumps(validated.model_dump())}],
        }
    except (json.JSONDecodeError, Exception) as e:
        return {
            "status": "error",
            "content": [{"text": f"Validation failed: {e}. Please fix and try again."}],
        }


SYSTEM_PROMPT = """\
You are a weather artist AI. Given a location (and optionally coordinates and a style prompt), \
you must fetch the real weather and produce a JSON object describing a p5.js scene that \
artistically represents the current weather conditions.

## Workflow
1. Call get_scene_format to learn the exact JSON schema, element types, and artistic guidelines.
2. If only a city name is given, call geocode_location to get coordinates.
3. Call get_weather with the latitude and longitude.
4. Based on the weather data and the scene format reference, produce the scene JSON.
5. Call validate_scene with your JSON to verify it is valid. If it fails, fix the errors and validate again.

Return ONLY the validated JSON as your final answer — no markdown fences, no explanation text.
"""


def extract_json_from_response(text: str) -> dict:
    """Extract and parse JSON from agent response, stripping markdown fences if present."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
    cleaned = re.sub(r"\n?```\s*$", "", cleaned)
    cleaned = cleaned.strip()
    return json.loads(cleaned)


def generate_scene(
    location: str,
    latitude: float | None = None,
    longitude: float | None = None,
    style_prompt: str = "",
) -> dict:
    """Generate a weather art scene for the given location.

    Creates a fresh Strands Agent, fetches weather data via tools, and returns
    a validated scene dict.
    """
    model = OllamaModel(
        host=OLLAMA_HOST,
        model_id=OLLAMA_MODEL_ID,
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[geocode_location, get_weather, get_scene_format, validate_scene],
    )

    if latitude is not None and longitude is not None:
        user_message = (
            f"Create a weather art scene for {location} "
            f"(latitude: {latitude}, longitude: {longitude})."
        )
    else:
        user_message = f"Create a weather art scene for {location}."

    if style_prompt:
        user_message += f" Style: {style_prompt}"

    result = agent(user_message)
    response_text = str(result)

    raw = extract_json_from_response(response_text)
    validated = SceneResponse.model_validate(raw)
    return validated.model_dump()