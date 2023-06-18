import logging
import os
from dataclasses import asdict, dataclass, field

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
    path: str

    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)


@dataclass
class Config:
    opened: list[Project] = field(default_factory=list)
    recent: list[Project] = field(default_factory=list)


class RecentProjects:
    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = Config()
        self._validator = fastjsonschema.compile(CONFIG_SCHEMA)
        self.load()

    def load(self):
        is_modified = False
        self._config = Config()
        if os.path.exists(self._config_path):
            with open(self._config_path, "r") as f:
                data = f.read()

            try:
                data = yaml.load(data, Loader=yaml.CLoader)
            except yaml.YAMLError:
                logger.error(f"Invalid YAML format for {self._config_path}")
                return

            try:
                self._validator(data)
            except fastjsonschema.JsonSchemaException:
                logger.error(f"Invalid structure for {self._config_path}")
                return

            for project in data.get("opened", []):
                if os.path.exists(project["path"]):
                    self._config.opened.append(Project(**project))
                else:
                    is_modified = True

            for project in data.get("recent", []):
                self._config.recent.append(Project(**project))

        if is_modified:
            self.dump()

    def dump(self):
        with open(self._config_path, "w") as f:
            f.write(yaml.dump(asdict(self._config), Dumper=yaml.CDumper))

    @property
    def opened(self) -> list[Project]:
        return self._config.opened

    @property
    def recent(self) -> list[Project]:
        return self._config.recent

    def add_opened(self, title: str, path: str):
        self.remove_opened(path, dump=False)
        self._config.opened.insert(0, Project(title, path))
        self.dump()

    def add_recent(self, title: str, path: str):
        self.remove_recent(path, dump=False)
        self._config.recent.insert(0, Project(title, path))
        self.dump()

    def remove_opened(self, path: str, dump: bool = True):
        for i, item in enumerate(self._config.opened):
            if item.path == path:
                self._config.opened.pop(i)
                break
        if dump:
            self.dump()

    def remove_recent(self, path: str, dump: bool = True):
        for i, item in enumerate(self._config.recent):
            if item.path == path:
                self._config.recent.pop(i)
                break
        if dump:
            self.dump()
