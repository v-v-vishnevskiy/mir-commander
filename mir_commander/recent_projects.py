import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger(__name__)


class Project(BaseModel):
    title: str = Field(min_length=1)
    path: Path

    @property
    def exists(self) -> bool:
        return self.path.exists()


class Config(BaseModel):
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


class RecentProjects:
    def __init__(self, config_path: Path):
        self._config_path = config_path
        self._config = self.load()
        self.dump()

    def load(self) -> Config:
        if self._config_path.exists():
            with self._config_path.open("r") as f:
                data = f.read()

            try:
                data = yaml.safe_load(data)
                if data:
                    return Config(**data)
            except yaml.YAMLError:
                logger.error("Invalid YAML format for %s", self._config_path)
            except ValidationError:
                logger.error("Invalid structure for %s", self._config_path)
        return Config()

    def dump(self):
        data = self._config.model_dump(exclude_defaults=True, mode="json")
        raw_data = yaml.safe_dump(data, allow_unicode=True)
        with self._config_path.open("w") as f:
            f.write(raw_data)

    @property
    def opened(self) -> list[Project]:
        return self._config.opened

    @property
    def recent(self) -> list[Project]:
        return self._config.recent

    def add_opened(self, title: str, path: Path):
        self.remove_opened(path, dump=False)
        self._config.opened.insert(0, Project(title=title, path=path))
        self.dump()

    def add_recent(self, title: str, path: Path):
        self.remove_recent(path, dump=False)
        self._config.recent.insert(0, Project(title=title, path=path))
        self.dump()

    def remove_opened(self, path: Path, dump: bool = True):
        for i, item in enumerate(self._config.opened):
            if item.path == path:
                self._config.opened.pop(i)
                break
        if dump:
            self.dump()

    def remove_recent(self, path: Path, dump: bool = True):
        for i, item in enumerate(self._config.recent):
            if item.path == path:
                self._config.recent.pop(i)
                break
        if dump:
            self.dump()
