import abc
from pathlib import Path
from typing import Callable

import yaml
from pydantic import BaseModel, Field

from mir_commander import errors


class BaseConfig(BaseModel, abc.ABC):
    path: None | Path = Field(default=None, exclude=True)

    @classmethod
    def load(cls, path: Path) -> "BaseConfig":
        if not path.exists():
            return cls(path=path)

        try:
            with path.open("r") as f:
                data = f.read()
        except IsADirectoryError:
            raise errors.ConfigError(f"Trying to load directory: {path}")

        if not data:
            return cls(path=path)

        try:
            return cls.model_validate(yaml.load(data, Loader=yaml.CLoader) | {"path": path}, strict=True)
        except yaml.YAMLError:
            raise errors.ConfigError(f"Invalid YAML format: {path}")

    def dump(self) -> None:
        if self.path is None:
            return

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(mode="json", exclude_defaults=True)
        raw_data = yaml.dump(data, Dumper=yaml.CDumper, allow_unicode=True)

        with self.path.open("w") as f:
            f.write(raw_data)
