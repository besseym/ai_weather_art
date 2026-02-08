# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Weather Art is a web application that uses an AI agent (Strands/Ollama with Llama 3.1) to generate animated p5.js visualizations based on real-time weather conditions. Users provide a location, the agent fetches weather data from Open-Meteo, and produces a declarative JSON that drives a p5.js scene renderer.

## Development Commands

- **Install dependencies**: `uv sync`
- **Run dev server**: `uv run flask --app app run --debug`
- **Run all tests**: `uv run pytest tests/ -v --cov=weather_art`
- **Run a single test file**: `uv run pytest tests/test_weather.py -v`
- **Docker build & run**: `docker compose up --build`

## Architecture

**Data flow**: User input (location + style prompt) → Geocoding API → Strands Agent (with Ollama) → Scene JSON → p5.js renderer → animated visualization

### Backend (Python/Flask)
- `app.py` — Flask entry point, registers blueprint
- `weather_art/config.py` — Environment-based config (OLLAMA_HOST, OLLAMA_MODEL_ID, Open-Meteo URLs)
- `weather_art/geocoding.py` — Open-Meteo Geocoding API client
- `weather_art/weather.py` — Open-Meteo Weather API client with WMO code mapping
- `weather_art/scene_schema.py` — Pydantic models defining the scene JSON format (discriminated unions via Literal type field for 9 element types)
- `weather_art/agent.py` — Strands agent with `@tool` decorated functions (`geocode_location`, `get_weather`), system prompt with full schema reference, JSON extraction/validation
- `weather_art/routes.py` — Flask Blueprint: `GET /`, `POST /api/generate`, `GET /api/geocode`

### Frontend (JavaScript)
- `static/js/renderer.js` — `WeatherArtRenderer` class using p5.js instance mode; handles all 9 element types including particle systems
- `static/js/app.js` — Geolocation, API calls, renderer integration
- `templates/index.html` — Bootstrap 5 dark theme UI

### Scene JSON Schema
The AI generates a declarative JSON with 9 element types: circle, ellipse, rect, line, triangle, arc, text, particle_system, glow. The `particle_system` type is the key animation primitive — it lets the AI describe weather effects (rain, snow, fog) declaratively rather than specifying individual particles. See `docs/implementation-plan.md` Phase 3 for full schema details.

### Key Design Decisions
- Fresh Agent instance per request (no conversation history, no thread-safety issues)
- JSON output from the AI is extracted by stripping markdown fences, then validated with Pydantic
- Retry logic on JSON parse failure (re-prompt once)
- Weather API: Open-Meteo (free, no auth key required)

## Implementation Plan

The project follows a 6-phase plan documented in `docs/implementation-plan.md`. Check this file for detailed requirements per phase.