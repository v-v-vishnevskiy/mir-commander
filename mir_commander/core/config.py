import abc
import logging
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from .errors import ConfigError

logger = logging.getLogger("Utils.Config")


class _CyFunctionDetectorMeta(type):
    def __instancecheck__(self, instance):
        return instance.__class__.__name__ == "cython_function_or_method"


class CyFunctionDetector(metaclass=_CyFunctionDetectorMeta):
    pass


class BaseModel(PydanticBaseModel):
    model_config = {"ignored_types": (CyFunctionDetector,)}


class BaseConfig(BaseModel, abc.ABC):
    path: None | Path = Field(default=None, exclude=True)

    @classmethod
    def load(cls, path: Path) -> Self:
        logger.debug(f"Loading config from {path} ...")
        if not path.exists():
            logger.debug("File does not exist. Loading defaults ...")
            return cls(path=path)

        if path.is_dir():
            raise ConfigError(f"Trying to load directory: {path}")

        with path.open("r") as f:
            data = f.read()

        if not data:
            return cls(path=path)

        try:
            parsed_data = yaml.load(data, Loader=yaml.CLoader)
        except yaml.YAMLError:
            raise ConfigError(f"Invalid YAML format: {path}")

        return cls.model_validate(parsed_data | {"path": path}, strict=True)

    def dump(self) -> None:
        logger.debug(f"Dumping config to {self.path} ...")
        if self.path is None:
            logger.debug("No path has been set")
            return

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(mode="json", exclude_defaults=True)
        raw_data = yaml.dump(data, Dumper=yaml.CDumper, allow_unicode=True)

        with self.path.open("w") as f:
            f.write(raw_data)
