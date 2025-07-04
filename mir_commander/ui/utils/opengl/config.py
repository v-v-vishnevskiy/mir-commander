from pydantic import BaseModel, Field

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
