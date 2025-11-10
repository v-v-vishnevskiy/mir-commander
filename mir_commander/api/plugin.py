from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field

from .metadata import Metadata


class PluginDependency(BaseModel):
    name: str = Field(min_length=1, description="Name of the dependency")
    version: str = ""
    type: Literal["python_package"]


class Plugin(ABC):
    @abstractmethod
    def get_metadata(self) -> Metadata: ...

    @abstractmethod
    def get_dependencies(self) -> list[PluginDependency]: ...
