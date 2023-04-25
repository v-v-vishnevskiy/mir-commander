import logging
import os
from typing import Any, Dict, List, Optional

import yaml

from mir_commander import exceptions

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, path: str, key: str = "", config: Optional["Config"] = None):
        self._root_data: Dict[str, Any] = {}

        if config:
            self._path: str = config._path
            self._root_data = config._root_data
            self._data: Dict[str, Any] = config._data
            self._data = self.get(key, {})
        else:
            self._path = os.path.normpath(path)
            self._load()
            self._data = self._root_data

    def _load(self):
        if os.path.exists(self._path):
            with open(self._path, "r") as f:
                data = f.read()

            if not data:
                return

            try:
                self._root_data = yaml.load(data, Loader=yaml.CLoader)
            except yaml.YAMLError:
                logger.error(f"Invalid YAML format for {self._path}")
                return

    def dump(self):
        with open(self._path, "w") as f:
            try:
                f.write(yaml.dump(self._root_data, Dumper=yaml.CDumper, default_flow_style=None))
            except yaml.YAMLError:
                pass

    def nested(self, key: str) -> "Config":
        return Config("", key, self)

    def _key(self, key: str) -> List[str]:
        if not isinstance(key, str):
            error = f"Invalid type key: {type(key)}"
            logger.error(error)
            raise exceptions.Config(error)

        if not key:
            error = "Empty key"
            logger.error(error)
            raise exceptions.Config(error)

        parts = key.split(".")
        for part in parts:
            if not part:
                error = "Empty part of key"
                logger.error(error)
                raise exceptions.Config(error)

        return parts

    def contains(self, key: str) -> bool:
        data = self._data
        try:
            for part in self._key(key):
                data = data[part]
            return True
        except KeyError:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        data = self._data
        try:
            for part in self._key(key):
                data = data[part]
            return data
        except KeyError:
            return default

    def set(self, key: str, value: Any):
        parts = self._key(key)
        data = self._data

        for i, part in enumerate(parts[:-1]):
            if part not in data:
                data[part] = {}
            elif not isinstance(data[part], dict):
                data[part] = {}
                logger.warning(f"""Replace value for '{".".join(parts[0:i + 1])}' path on object""")
            data = data[part]

        data[parts[-1]] = value

        self.dump()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)
