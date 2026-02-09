from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, model_validator


# --- Background types ---

class SolidBackground(BaseModel):
    type: Literal["solid"] = "solid"
    color: str


class GradientBackground(BaseModel):
    type: Literal["gradient"] = "gradient"
    colors: list[str] = Field(min_length=2)
    direction: Literal["vertical", "horizontal"] = "vertical"


Background = Annotated[
    Union[SolidBackground, GradientBackground],
    Field(discriminator="type"),
]


# --- Element types ---

class Ellipse(BaseModel):
    type: Literal["ellipse"] = "ellipse"
    x: float
    y: float
    width: float
    height: float
    fill: str | None = None
    stroke: str | None = None
    stroke_weight: float = 1.0
    opacity: float = 1.0


class Rect(BaseModel):
    type: Literal["rect"] = "rect"
    x: float
    y: float
    width: float
    height: float
    fill: str | None = None
    stroke: str | None = None
    corner_radius: float = 0.0
    opacity: float = 1.0


class Line(BaseModel):
    type: Literal["line"] = "line"
    x1: float
    y1: float
    x2: float
    y2: float
    stroke: str = "#ffffff"
    stroke_weight: float = 1.0
    opacity: float = 1.0


class TextElement(BaseModel):
    type: Literal["text"] = "text"
    content: str
    x: float
    y: float
    size: float = 16.0
    fill: str = "#ffffff"
    opacity: float = 1.0


# --- Particle presets ---

PARTICLE_PRESETS: dict[str, dict] = {
    "rain": {
        "particle_shape": "line",
        "count": 200,
        "speed": 5.0,
        "angle": 260.0,
        "drift": 0.5,
        "size": 4.0,
        "opacity": 0.6,
    },
    "snow": {
        "particle_shape": "circle",
        "count": 150,
        "speed": 1.5,
        "angle": 270.0,
        "drift": 1.5,
        "size": 4.0,
        "opacity": 0.8,
    },
    "fog": {
        "particle_shape": "circle",
        "count": 80,
        "speed": 0.5,
        "angle": 180.0,
        "drift": 0.0,
        "size": 20.0,
        "opacity": 0.3,
    },
    "dust": {
        "particle_shape": "circle",
        "count": 50,
        "speed": 1.0,
        "angle": 200.0,
        "drift": 2.0,
        "size": 2.0,
        "opacity": 0.5,
    },
    "stars": {
        "particle_shape": "circle",
        "count": 100,
        "speed": 0.0,
        "angle": 0.0,
        "drift": 0.0,
        "size": 2.0,
        "opacity": 0.9,
    },
}


class ParticleSystem(BaseModel):
    type: Literal["particle_system"] = "particle_system"
    preset: Literal["rain", "snow", "fog", "dust", "stars"]
    color: str = "#ffffff"
    count: int | None = Field(default=None, ge=1, le=1000)
    opacity: float | None = None
    speed: float | None = None
    particle_shape: Literal["circle", "line", "rect"] | None = None
    angle: float | None = None
    drift: float | None = None
    size: float | None = None

    @model_validator(mode="before")
    @classmethod
    def apply_preset(cls, values: dict) -> dict:
        preset_name = values.get("preset")
        if preset_name and preset_name in PARTICLE_PRESETS:
            defaults = PARTICLE_PRESETS[preset_name]
            for key, default_val in defaults.items():
                if values.get(key) is None:
                    values[key] = default_val
        return values


class Glow(BaseModel):
    type: Literal["glow"] = "glow"
    x: float
    y: float
    radius: float
    color: str = "#ffffff"
    intensity: float = 0.5


Element = Annotated[
    Union[Ellipse, Rect, Line, TextElement, ParticleSystem, Glow],
    Field(discriminator="type"),
]


# --- Scene structure ---

class Canvas(BaseModel):
    width: int = 800
    height: int = 600


class Metadata(BaseModel):
    title: str = ""
    weather_summary: str = ""


class Scene(BaseModel):
    canvas: Canvas = Field(default_factory=Canvas)
    background: Background = Field(default_factory=lambda: SolidBackground(color="#000000"))
    elements: list[Element] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=Metadata)


class SceneResponse(BaseModel):
    scene: Scene