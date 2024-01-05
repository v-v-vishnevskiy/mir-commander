import logging
from pathlib import Path
from typing import Any, Optional

import yaml

from mir_commander import exceptions

logger = logging.getLogger(__name__)


class Config:
    def __init__(
        self, path: None | Path = None, key: str = "", parent: Optional["Config"] = None, read_only: bool = False
    ) -> None:
        self._path = path
        self._data: dict[str, Any] = {}
        self._nested_key = key
        self._defaults: None | "Config" = None
        self._parent = parent
        self._read_only = read_only

        if self._path:
            self._path = self._path.resolve()

        if parent is None:
            self._load()

    def _key(self, key: str) -> list[str]:
        if not isinstance(key, str):
            raise exceptions.ConfigKey(f"Invalid type: {type(key)}")

        if not key:
            raise exceptions.ConfigKey("Empty")

        parts = key.split(".")
        for part in parts:
            if not part:
                raise exceptions.ConfigKey("Empty part")

        return parts

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
                self._data = yaml.load(data, Loader=yaml.CLoader)
            except yaml.YAMLError:
                logger.error(f"Invalid YAML format: {self._path}")
                return

    def set_defaults(self, config: "Config") -> None:
        if self._parent is None:
            self._defaults = config
        else:
            raise exceptions.Config("Can't set defaults for nested config")

    def dump(self) -> None:
        if self._parent is not None:
            self._parent.dump()
        elif self._path is not None and self._read_only is False:
            if not self._path.exists():
                Path(self._path.parts[0]).mkdir(parents=True, exist_ok=True)
            data = yaml.dump(self._data, Dumper=yaml.CDumper, allow_unicode=True)
            with self._path.open("w") as f:
                f.write(data)

    def nested(self, key: str) -> "Config":
        return Config(self._path, key=key, parent=self, read_only=self._read_only)

    def contains(self, key: str) -> bool:
        """Checks whether exist value with that key.

        :param key: a sequence of keys split by dot "." sign. Example: "widgets.toolbars.icon_size"
        :return: returns True if values exists by presented key else returns False
        """
        if self._parent is not None:
            return self._parent.contains(f"{self._nested_key}.{key}")
        else:
            data = self._data
            try:
                for part in self._key(key):
                    data = data[part]
                return True
            except KeyError:
                if self._defaults:
                    return self._defaults.contains(key)
                return False
            except TypeError:
                return False

    def get(self, key: str, default: Any = None) -> Any:
        if self._parent is not None:
            return self._parent.get(f"{self._nested_key}.{key}", default)
        else:
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
        if self._parent is not None:
            self._parent.set(f"{self._nested_key}.{key}", value, write)
        else:
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

            if write:
                self.dump()

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.set(key, value, False)

    def __repr__(self) -> str:
        if self._nested_key:
            return f'{self.__class__.__name__}("{self._path}", key="{self._nested_key}", read_only={self._read_only})'
        else:
            return f'{self.__class__.__name__}("{self._path}", read_only={self._read_only})'
