from abc import ABC, abstractmethod

from .metadata import Metadata


class ProjectNodePlugin(ABC):
    @abstractmethod
    def get_metadata(self) -> Metadata: ...

    @abstractmethod
    def get_type(self) -> str: ...

    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_icon_path(self) -> str: ...
