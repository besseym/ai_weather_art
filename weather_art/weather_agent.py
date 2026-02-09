from strands import Agent
from strands.models import OllamaModel

from weather_art.agent import geocode_location, get_weather
from weather_art.config import OLLAMA_HOST, OLLAMA_MODEL_ID

SYSTEM_PROMPT = """\
You are a weather reporter. Given a location, use your tools to look up the \
current weather conditions and return a concise, vivid natural-language description.

## Workflow
1. If given a city name, call geocode_location to get coordinates.
2. Call get_weather with the latitude and longitude.
3. Return a short weather description (2-4 sentences) covering temperature, \
conditions, wind, and any precipitation. Include the location name.

Return ONLY the weather description — no JSON, no extra formatting.
"""


def describe_weather(user_message: str) -> str:
    """Get a natural-language weather description for a location.

    Creates a fresh Strands Agent, fetches weather data via tools, and returns
    a human-readable description.

    Args:
        user_message: The user's request, e.g. "Describe the current weather in Berlin."
    """
    model = OllamaModel(
        host=OLLAMA_HOST,
        model_id=OLLAMA_MODEL_ID,
    )

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[geocode_location, get_weather],
    )

    result = agent(user_message)
    return str(result).strip()
