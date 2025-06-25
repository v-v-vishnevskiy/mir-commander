from pydantic import BaseModel, Field


class Tree(BaseModel):
    icon_size: int = Field(default=20, ge=16, le=32, description="Icon size in pixels")


class ProjectDock(BaseModel):
    tree: Tree = Tree()


class DocksConfig(BaseModel):
    project: ProjectDock = ProjectDock()
