import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://192.168.86.143:41969")
OLLAMA_MODEL_ID = os.environ.get("OLLAMA_MODEL_ID", "llama3.2")

OPEN_METEO_GEOCODING_URL = os.environ.get(
    "OPEN_METEO_GEOCODING_URL", "https://geocoding-api.open-meteo.com/v1/search"
)
OPEN_METEO_FORECAST_URL = os.environ.get(
    "OPEN_METEO_FORECAST_URL", "https://api.open-meteo.com/v1/forecast"
)
