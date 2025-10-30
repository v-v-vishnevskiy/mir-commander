from abc import ABC, abstractmethod

from pydantic import BaseModel

from .metadata import Metadata


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

    @abstractmethod
    def get_metadata(self) -> Metadata: ...
