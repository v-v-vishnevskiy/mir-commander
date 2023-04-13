import json
import logging
import os
from dataclasses import asdict, dataclass, field
from typing import List, Union

import fastjsonschema

logger = logging.getLogger(__name__)


CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": True,
    "properties": {
        "last_opened": {
            "type": "object",
            "additionalProperties": False,
            "properties": {"title": {"type": "string", "minLength": 1}, "path": {"type": "string", "minLength": 1}},
            "required": ["title", "path"],
        },
        "recent": {
            "type": "array",
            "item": {
                "type": "object",
                "additionalProperties": False,
                "properties": {"title": {"type": "string", "minLength": 1}, "path": {"type": "string", "minLength": 1}},
                "required": ["title", "path"],
            },
            "minItems": 0,
        },
    },
}


@dataclass
class Project:
    title: str
    path: str


@dataclass
class Config:
    last_opened: Union[None, Project] = None
    recent: List[Project] = field(default_factory=list)


class RecentProjects:
    def __init__(self, config_path: str):
        self._config_path = config_path
        self._config = Config()
        self._validator = fastjsonschema.compile(CONFIG_SCHEMA)
        self.load()

    def load(self):
        if os.path.exists(self._config_path):
            with open(self._config_path, "r") as f:
                data = f.read()

            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format for {self._config_path}")
                return

            try:
                self._validator(data)
            except fastjsonschema.JsonSchemaException:
                logger.error(f"Invalid structure for {self._config_path}")
                return

            if "last_opened" in data:
                self._config.last_opened = Project(**data["last_opened"])

            for project in data.get("recent", []):
                self._config.recent.append(Project(**project))

    def dump(self):
        with open(self._config_path, "w") as f:
            f.write(json.dumps(asdict(self._config), indent=4))

    def last_opened(self) -> Union[None, Project]:
        return self._config.last_opened

    def recent(self) -> List[Project]:
        return self._config.recent

    def set_last_opened(self, project: Project):
        self._config.last_opened = project

    def add_recent(self, project: Project):
        for i, recent in enumerate(self._config.recent):
            if recent.path == project.path:
                self._config.recent.pop(i)
                break
        self._config.recent.insert(0, project)

    def unset_last_opened(self):
        self._config.last_opened = None

    def pop_recent(self, index: int) -> Project:
        return self._config.recent.pop(index)
