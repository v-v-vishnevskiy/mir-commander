from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from mir_commander.base_config import BaseConfig


class Project(BaseModel):
    title: str = Field(min_length=1)
    path: Path

    @property
    def exists(self) -> bool:
        return self.path.exists()


class RecentProjectsConfig(BaseConfig):
    opened: list[Project] = []
    recent: list[Project] = []

    @field_validator("opened", "recent", mode="after")
    @classmethod
    def _check_exists(cls, v: list[Project]) -> list[Project]:
        result = []
        for p in v:
            if p.exists:
                result.append(p)
        return result

    def add_opened(self, title: str, path: Path):
        self.remove_opened(path, dump=False)
        self.opened.insert(0, Project(title=title, path=path))
        self.dump()

    def add_recent(self, title: str, path: Path):
        self.remove_recent(path, dump=False)
        self.recent.insert(0, Project(title=title, path=path))
        self.dump()

    def remove_opened(self, path: Path, dump: bool = True):
        for i, item in enumerate(self.opened):
            if item.path == path:
                self.opened.pop(i)
                break
        if dump:
            self.dump()

    def remove_recent(self, path: Path, dump: bool = True):
        for i, item in enumerate(self.recent):
            if item.path == path:
                self.recent.pop(i)
                break
        if dump:
            self.dump()
