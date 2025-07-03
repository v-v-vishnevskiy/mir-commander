from pydantic import BaseModel, Field


class TreeConfig(BaseModel):
    icon_size: int = Field(default=20, ge=16, le=32, description="Icon size in pixels")


class ProjectDockConfig(BaseModel):
    tree: TreeConfig = TreeConfig()
