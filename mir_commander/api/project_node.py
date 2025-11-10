from abc import abstractmethod

from .plugin import Plugin


class ProjectNodePlugin(Plugin):
    @abstractmethod
    def get_type(self) -> str: ...

    @abstractmethod
    def get_icon_path(self) -> str: ...
