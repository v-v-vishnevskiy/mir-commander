from pydantic import BaseModel

from .project_dock.config import ProjectDockConfig


class DocksConfig(BaseModel):
    project: ProjectDockConfig = ProjectDockConfig()
