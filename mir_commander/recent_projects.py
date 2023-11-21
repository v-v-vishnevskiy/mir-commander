import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path

import fastjsonschema
import yaml

logger = logging.getLogger(__name__)


LIST_PROJECTS = {
    "type": "array",
    "items": {
        "type": "object",
        "additionalProperties": False,
        "properties": {"title": {"type": "string", "minLength": 1}, "path": {"type": "string", "minLength": 1}},
        "required": ["title", "path"],
    },
    "minItems": 0,
}


CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {"opened": LIST_PROJECTS, "recent": LIST_PROJECTS},
}


@dataclass
class Project:
    title: str
    path: Path

    @property
    def exists(self) -> bool:
        return self.path.exists()


@dataclass
class Config:
    opened: list[Project] = field(default_factory=list)
    recent: list[Project] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = asdict(self)
        for entity in ("opened", "recent"):
            for item in result[entity]:
                item["path"] = str(item["path"])
        return result


class RecentProjects:
    def __init__(self, config_path: Path):
        self._config_path = config_path
        self._config = Config()
        self._validator = fastjsonschema.compile(CONFIG_SCHEMA)
        self.load()

    def load(self):
        is_modified = False
        self._config = Config()
        if self._config_path.exists():
            with self._config_path.open("r") as f:
                data = f.read()

            try:
                data = yaml.safe_load(data)
            except yaml.YAMLError:
                logger.error(f"Invalid YAML format for {self._config_path}")
                return

            try:
                self._validator(data)
            except fastjsonschema.JsonSchemaException:
                logger.error(f"Invalid structure for {self._config_path}")
                return

            for project in data.get("opened", []):
                project["path"] = Path(project["path"])
                if project["path"].exists():
                    self._config.opened.append(Project(**project))
                else:
                    is_modified = True

            for project in data.get("recent", []):
                project["path"] = Path(project["path"])
                self._config.recent.append(Project(**project))

        if is_modified:
            self.dump()

    def dump(self):
        with self._config_path.open("w") as f:
            f.write(yaml.safe_dump(self._config.to_dict(), allow_unicode=True))

    @property
    def opened(self) -> list[Project]:
        return self._config.opened

    @property
    def recent(self) -> list[Project]:
        return self._config.recent

    def add_opened(self, title: str, path: Path):
        self.remove_opened(path, dump=False)
        self._config.opened.insert(0, Project(title, path))
        self.dump()

    def add_recent(self, title: str, path: Path):
        self.remove_recent(path, dump=False)
        self._config.recent.insert(0, Project(title, path))
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
