import logging
from pathlib import Path
from typing import Any, Optional

import yaml

from mir_commander import exceptions

logger = logging.getLogger(__name__)


class Config:
    def __init__(
        self, path: None | Path = None, key: str = "", config: Optional["Config"] = None, read_only: bool = False
    ):
        self._path = path
        self._root_data: dict[str, Any] = {}
        self._nested_key = key
        self._synced = True
        self._defaults: Optional["Config"] = None
        self._read_only = read_only

        if self._path:
            self._path = self._path.resolve()

        if config:
            self._root_data = config._root_data
            self._data: dict[str, Any] = config._data
            if not self.contains(key):
                self.set(key, {})
            self._data = self.get(key)
        else:
            self._load()
            self._data = self._root_data

    def _load(self) -> None:
        if self._path is not None and self._path.exists():
            try:
                with self._path.open("r") as f:
                    data = f.read()
            except IsADirectoryError:
                logger.error(f"Trying to load directory: {self._path}")
                return

            if not data:
                return

            try:
                self._root_data = yaml.load(data, Loader=yaml.CLoader)
            except yaml.YAMLError:
                logger.error(f"Invalid YAML format: {self._path}")
                return

    @property
    def synced(self) -> bool:
        return self._synced

    def set_data(self, data: dict) -> None:
        self._data = data

    def set_defaults(self, config: "Config") -> None:
        self._defaults = config

    def dump(self) -> None:
        if self._path is not None and self._read_only is False:
            if not self._path.exists():
                Path(self._path.parts[0]).mkdir(parents=True, exist_ok=True)
            try:
                with self._path.open("w") as f:
                    try:
                        f.write(yaml.dump(self._root_data, Dumper=yaml.CDumper, allow_unicode=True))
                    except yaml.YAMLError:
                        raise
            except IsADirectoryError:
                logger.error(f"Trying to load directory: {self._path}")
        self._synced = True

    def nested(self, key: str) -> "Config":
        config = Config(self._path, key, self, read_only=self._read_only)
        if self._defaults:
            config.set_defaults(self._defaults.nested(key))
        return config

    def _key(self, key: str) -> list[str]:
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
            if self._defaults:
                return self._defaults.get(key, default)
            else:
                return default

    def set(self, key: str, value: Any, write: bool = True) -> None:
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

        if self._path:
            self._synced = False

        if write:
            self.dump()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value, False)

    def __repr__(self) -> str:
        if self._nested_key:
            return f'{self.__class__.__name__}("{self._path}", "{self._nested_key}", read_only={self._read_only})'
        else:
            return f'{self.__class__.__name__}("{self._path}", read_only={self._read_only})'
