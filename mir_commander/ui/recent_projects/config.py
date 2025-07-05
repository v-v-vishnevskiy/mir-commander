from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from mir_commander.utils.config import BaseConfig
from mir_commander.core import Project


class ProjectConfig(BaseModel):
    name: str = Field(min_length=1)
    path: Path

    @field_validator("path", mode="before")
    @classmethod
    def _path_converter(cls, v: str | Path) -> Path:
        if type(v) is str:
            return Path(v)
        return v

    @property
    def exists(self) -> bool:
        return self.path.exists()


class RecentProjectsConfig(BaseConfig):
    opened: list[ProjectConfig] = []
    recent: list[ProjectConfig] = []

    @field_validator("opened", "recent", mode="after")
    @classmethod
    def _check_exists(cls, v: list[ProjectConfig]) -> list[ProjectConfig]:
        result = []
        for p in v:
            if p.exists:
                result.append(p)
        return result

    def add_opened(self, project: Project):
        self.remove_opened(project.path, dump=False)
        self.opened.insert(0, ProjectConfig(name=project.name, path=project.path))
        self.dump()

    def add_recent(self, project: Project):
        self.remove_recent(project.path, dump=False)
        self.recent.insert(0, ProjectConfig(name=project.name, path=project.path))
        self.dump()

    def remove_opened(self, project: Project, dump: bool = True):
        for i, item in enumerate(self.opened):
            if item.path == project.path:
                self.opened.pop(i)
                break
        if dump:
            self.dump()

    def remove_recent(self, project: Project, dump: bool = True):
        for i, item in enumerate(self.recent):
            if item.path == project.path:
                self.recent.pop(i)
                break
        if dump:
            self.dump()
