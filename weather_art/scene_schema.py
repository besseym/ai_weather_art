from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


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

class Circle(BaseModel):
    type: Literal["circle"] = "circle"
    x: float
    y: float
    radius: float
    fill: str | None = None
    stroke: str | None = None
    stroke_weight: float = 1.0
    opacity: float = 1.0


class Ellipse(BaseModel):
    type: Literal["ellipse"] = "ellipse"
    x: float
    y: float
    width: float
    height: float
    fill: str | None = None
    stroke: str | None = None
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


class Triangle(BaseModel):
    type: Literal["triangle"] = "triangle"
    x1: float
    y1: float
    x2: float
    y2: float
    x3: float
    y3: float
    fill: str | None = None
    stroke: str | None = None
    opacity: float = 1.0


class Arc(BaseModel):
    type: Literal["arc"] = "arc"
    x: float
    y: float
    width: float
    height: float
    start_angle: float
    stop_angle: float
    stroke: str = "#ffffff"
    stroke_weight: float = 2.0
    fill: str | None = None
    opacity: float = 1.0


class TextElement(BaseModel):
    type: Literal["text"] = "text"
    content: str
    x: float
    y: float
    size: float = 16.0
    fill: str = "#ffffff"
    opacity: float = 1.0


class ParticleRegion(BaseModel):
    x: float = 0.0
    y: float = 0.0
    width: float = 800.0
    height: float = 600.0


class ParticleSystem(BaseModel):
    type: Literal["particle_system"] = "particle_system"
    particle_shape: Literal["circle", "line", "rect"] = "circle"
    count: int = Field(default=100, ge=1, le=1000)
    region: ParticleRegion = Field(default_factory=ParticleRegion)
    speed: float = 2.0
    angle: float = 270.0
    drift: float = 0.0
    size: float = 3.0
    color: str = "#ffffff"
    opacity: float = 1.0


class Glow(BaseModel):
    type: Literal["glow"] = "glow"
    x: float
    y: float
    radius: float
    color: str = "#ffffff"
    intensity: float = 0.5


Element = Annotated[
    Union[Circle, Ellipse, Rect, Line, Triangle, Arc, TextElement, ParticleSystem, Glow],
    Field(discriminator="type"),
]


# --- Scene structure ---

class Canvas(BaseModel):
    width: int = 800
    height: int = 600


class Metadata(BaseModel):
    title: str = ""
    weather_summary: str = ""


class Layer(BaseModel):
    id: str
    opacity: float = 1.0
    elements: list[Element] = Field(default_factory=list)


class Scene(BaseModel):
    canvas: Canvas = Field(default_factory=Canvas)
    background: Background = Field(default_factory=lambda: SolidBackground(color="#000000"))
    layers: list[Layer] = Field(default_factory=list)
    metadata: Metadata = Field(default_factory=Metadata)


class SceneResponse(BaseModel):
    scene: Scene