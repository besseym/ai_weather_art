# AI Weather Art - Implementation Plan

## Context

The project is an AI agent that generates p5.js art based on real-time weather conditions. A user provides a location (city name or browser geolocation), the Strands/Ollama agent fetches weather data from Open-Meteo, and produces a declarative JSON that drives an animated p5.js visualization. Currently the project is a bare Flask skeleton with only a "Hello World" route.

## Target Project Structure

```
ai_weather_art/
  app.py                        # Flask entry point (modify existing)
  pyproject.toml                # Dependencies (modify existing)
  Dockerfile
  docker-compose.yml
  .env.example
  .dockerignore
  weather_art/
    __init__.py
    config.py                   # Ollama/API configuration
    weather.py                  # Open-Meteo weather client
    geocoding.py                # Open-Meteo geocoding client
    scene_schema.py             # Pydantic models for the scene JSON
    agent.py                    # Strands agent, tools, system prompt
    routes.py                   # Flask blueprint with API routes
  static/
    js/
      renderer.js               # p5.js scene renderer
      app.js                    # Frontend logic
    css/
      style.css                 # Minimal overrides (Bootstrap handles general styles)
  templates/
    index.html
  tests/
    __init__.py                 # (exists)
    conftest.py
    test_weather.py
    test_geocoding.py
    test_scene_schema.py
    test_agent.py
    test_routes.py
```

---

## Phase 1 - Foundation: Dependencies, Config, Docker

### Files to create/modify

- **`pyproject.toml`** (modify) - Add dependencies: `strands-agents[ollama]`, `requests`, `pydantic`, `python-dotenv`, and dev deps `pytest`, `pytest-cov`
- **`weather_art/__init__.py`** (create) - Empty package init
- **`weather_art/config.py`** (create) - Constants: `OLLAMA_HOST`, `OLLAMA_MODEL_ID`, Open-Meteo URLs, loaded from env vars with defaults
- **`.env.example`** (create) - Template with `OLLAMA_HOST` and `OLLAMA_MODEL_ID`
- **`Dockerfile`** (create) - Python 3.14-slim, uv sync, expose 5000
- **`docker-compose.yml`** (create) - Two services: `ollama` (ollama/ollama image) and `web` (Flask app, depends on ollama)
- **`.dockerignore`** (create) - Exclude `.venv`, `.idea`, `__pycache__`, `.git`

### Verify
- `uv sync` installs all dependencies
- `docker compose build` succeeds

---

## Phase 2 - Weather Integration: Open-Meteo Clients

### Files to create

- **`weather_art/geocoding.py`** - `geocode_city(city_name: str) -> dict` - Calls Open-Meteo Geocoding API, returns `{name, latitude, longitude, country, timezone}`. Raises `ValueError` if not found.

- **`weather_art/weather.py`** - `get_current_weather(lat, lon) -> dict` - Calls Open-Meteo Forecast API with `current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,cloud_cover,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation,rain,snowfall,is_day`. Includes a `WMO_CODES` dict to map weather codes to human descriptions. Returns a clean dict with keys like `temperature_c`, `humidity_pct`, `weather_description`, `is_day`, etc.

- **`tests/test_geocoding.py`** and **`tests/test_weather.py`** - Unit tests with mocked `requests.get`

### Verify
- `uv run pytest tests/test_geocoding.py tests/test_weather.py -v`
- Manual: `python -c "from weather_art.weather import get_current_weather; print(get_current_weather(52.52, 13.41))"`

---

## Phase 3 - Scene Schema & p5.js Renderer

This is the core interface between the AI and the frontend.

### Scene JSON Schema

```json
{
  "scene": {
    "canvas": {"width": 800, "height": 600},
    "background": {"type": "gradient", "colors": ["#1a1a2e", "#0f3460"], "direction": "vertical"},
    "layers": [
      {
        "id": "sky_objects",
        "opacity": 1.0,
        "elements": [...]
      }
    ],
    "metadata": {"title": "Rainy Evening", "weather_summary": "Rain, 8C, wind 25km/h"}
  }
}
```

**9 element types** (kept small for reliable AI generation):

| Type | Purpose | Key fields |
|------|---------|------------|
| `circle` | Sun, moon, dots | x, y, radius, fill, stroke, opacity |
| `ellipse` | Clouds | x, y, width, height, fill, opacity |
| `rect` | Ground, buildings | x, y, width, height, fill, cornerRadius, opacity |
| `line` | Lightning, streaks | x1, y1, x2, y2, stroke, strokeWeight, opacity |
| `triangle` | Mountains, trees | x1,y1, x2,y2, x3,y3, fill, opacity |
| `arc` | Rainbows | x, y, width, height, startAngle, stopAngle, stroke, opacity |
| `text` | Labels | content, x, y, size, fill, opacity |
| `particle_system` | Rain, snow, fog | particle_shape, count, region, speed, angle, drift, color, opacity |
| `glow` | Sun/moon glow | x, y, radius, color, intensity |

The `particle_system` is key -- it lets the AI say "200 rain drops at angle 260" instead of specifying hundreds of individual elements. The renderer instantiates and animates particles automatically.

### Files to create

- **`weather_art/scene_schema.py`** - Pydantic models: `SolidBackground`, `GradientBackground`, `Circle`, `Ellipse`, `Rect`, `Line`, `Triangle`, `Arc`, `TextElement`, `ParticleSystem`, `Glow`, `Layer`, `Canvas`, `Metadata`, `Scene`, `SceneResponse`. Uses discriminated unions (`Literal` type field) for element dispatch.

- **`static/js/renderer.js`** - `WeatherArtRenderer` class using p5.js instance mode. Methods: `render(sceneJSON)`, `_setup(p)`, `_draw(p)`, `_drawBackground()`, `_drawElement()` (dispatches on type), `_initParticles()`, `_updateAndDrawParticles()`. Particle objects track position/velocity and wrap around edges.

- **`tests/test_scene_schema.py`** - Validate that good scene JSON passes, bad JSON rejects

### Verify
- Create a hand-written test scene JSON (sunny day) and render it via a temporary test route
- Visually confirm gradient bg, sun circle with glow, cloud ellipses, animated rain particles

---

## Phase 4 - AI Agent: Strands + Ollama

### Files to create

- **`weather_art/agent.py`** - Core module containing:
  - `@tool` decorated functions: `geocode_location(city_name)` and `get_weather(latitude, longitude)` wrapping the Phase 2 clients
  - `SYSTEM_PROMPT` - Detailed instructions explaining the scene JSON schema, all 9 element types, color guidelines, weather-to-visual mapping suggestions (e.g., rain = particle_system with line shape at angle 260), and artistic guidelines
  - `generate_scene(location, latitude, longitude, style_prompt) -> dict` - Creates a Strands `Agent` with `OllamaModel`, the two tools, and the system prompt. Sends the prompt, extracts JSON from the response (handling markdown fences), validates with Pydantic, returns the scene dict
  - `extract_json_from_response(text) -> dict` - Helper to strip markdown fences and parse JSON

### Key design decisions
- Fresh Agent per request (no conversation history accumulation, no thread-safety issues)
- System prompt includes the complete schema reference so the model knows exactly what to produce
- JSON extraction handles markdown fences (```json ... ```)
- Pydantic validation catches malformed output with clear errors

### Verify
- Start Ollama, pull llama3.1
- `python -c "from weather_art.agent import generate_scene; print(generate_scene('Berlin'))"`

---

## Phase 5 - Web UI & Flask Routes

### Files to create/modify

- **`weather_art/routes.py`** - Flask Blueprint with:
  - `GET /` - Serve `index.html`
  - `POST /api/generate` - Accept `{location, latitude, longitude, style_prompt}`, call `generate_scene()`, return scene JSON
  - `GET /api/geocode?city=Berlin` - Geocode a city name, return coordinates

- **`app.py`** (modify) - Register the blueprint, add `load_dotenv()`

- **`templates/index.html`** - Single page using **Bootstrap 5** components: `container` layout, `input-group` for location field + "Use My Location" button, `form-control` for style prompt input, `btn btn-primary` for Generate Art, Bootstrap `spinner-border` for loading state, `card` for the p5.js canvas container, `alert` for errors, metadata displayed in a `card-footer`. Includes Bootstrap CSS/JS from CDN, p5.js from CDN, + local `renderer.js` and `app.js`. Dark theme via Bootstrap's `data-bs-theme="dark"`.

- **`static/js/app.js`** - Frontend logic: geolocation handling, POST to `/api/generate`, pass response to `WeatherArtRenderer.render()`, toggle Bootstrap spinner visibility and alert components for loading/error states

- **`static/css/style.css`** - Minimal custom overrides only (canvas container sizing, any Bootstrap gaps). All general styling handled by Bootstrap.

- **`tests/test_routes.py`** - Flask test client tests for all endpoints

### Verify
- `uv run flask --app app run --debug`
- Open `http://localhost:5000`, enter "Berlin", click Generate Art
- Animated weather visualization appears after agent inference

---

## Phase 6 - Polish & Testing

- Add retry logic in `agent.py` if JSON parsing fails (re-prompt the agent once)
- Graceful handling of unknown element types in `renderer.js` (skip with console warning)
- **`tests/conftest.py`** - Shared fixtures: Flask test client, sample scene JSON, mock weather data
- Add pytest markers in `pyproject.toml` for `integration` tests
- Docker healthcheck and `.dockerignore` refinements
- Run full test suite: `uv run pytest tests/ -v --cov=weather_art`
- End-to-end test: `docker compose up --build`, test in browser

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Llama produces invalid JSON | Detailed system prompt, JSON fence stripping, Pydantic validation, retry logic |
| Visually poor scenes | System prompt with explicit weather-to-visual mappings and color palettes |
| Slow inference (30-90s) | Loading spinner in UI, concise system prompt |
| Tool calling issues with Ollama | Fallback: call weather API directly in Python, pass data in prompt instead of using tools |