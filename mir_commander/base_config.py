import abc
import logging
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from mir_commander import errors

logger = logging.getLogger("BaseConfig")


class BaseConfig(BaseModel, abc.ABC):
    path: None | Path = Field(default=None, exclude=True)

    @classmethod
    def load(cls, path: Path) -> "BaseConfig":
        logger.debug(f"Loading config from {path}...")
        if not path.exists():
            logger.debug("File doesn't exists. Loading defaults...")
            return cls(path=path)

        if path.is_dir():
            raise errors.ConfigError(f"Trying to load directory: {path}")

        with path.open("r") as f:
            data = f.read()

        if not data:
            return cls(path=path)

        try:
            parsed_data = yaml.load(data, Loader=yaml.CLoader)
        except yaml.YAMLError:
            raise errors.ConfigError(f"Invalid YAML format: {path}")

        return cls.model_validate(parsed_data | {"path": path}, strict=True)

    def dump(self) -> None:
        logger.debug(f"Dumping config to {self.path}...")
        if self.path is None:
            logger.debug("The path is not set")
            return

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(mode="json", exclude_defaults=True)
        raw_data = yaml.dump(data, Dumper=yaml.CDumper, allow_unicode=True)

        with self.path.open("w") as f:
            f.write(raw_data)
