from typing import Literal

from pydantic import BaseModel, Field
from pydantic_extra_types.color import Color

from .enums import ProjectionMode


class PerspectiveProjection(BaseModel):
    fov: float = Field(default=45.0, ge=35.0, le=90.0)


class OrthographicProjection(BaseModel):
    view_bounds: float = 5.4
    depth_factor: float = 10.0


class ProjectionConfig(BaseModel):
    mode: ProjectionMode = ProjectionMode.Perspective
    perspective: PerspectiveProjection = PerspectiveProjection()
    orthographic: OrthographicProjection = OrthographicProjection()


class TextOverlayConfig(BaseModel):
    position: list[int] = Field(default=[0, 0], min_length=2, max_length=2)
    font_size: int = 13
    font_bold: bool = False
    font_family: str = "Arial"
    color: Color = Color("#C8C8C8")
    background_color: Color = Color("#00000000")
    text_alignment: list[Literal["left", "right", "top", "bottom", "center"]] = Field(
        default_factory=lambda: ["left", "top"], 
        min_length=1, 
        max_length=2,
        description="Alignment of the text overlay. Can be a combination of 'left', 'right', 'top', 'bottom', 'center'"
    )
