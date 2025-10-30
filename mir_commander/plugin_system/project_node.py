from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Self

from pydantic import BaseModel


@dataclass
class ProjectNodeSchema:
    name: str
    type: str
    data: Any = field(default=None)
    nodes: list[Self] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ProjectNodeDataPlugin(BaseModel): ...


class ProjectNodePlugin(ABC):
    @abstractmethod
    def get_type(self) -> str: ...

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_icon_path(self) -> str: ...

    @abstractmethod
    def get_model_class(self) -> type[ProjectNodeDataPlugin]: ...

    @abstractmethod
    def get_default_program_name(self) -> None | str: ...

    @abstractmethod
    def get_program_names(self) -> list[str]: ...
