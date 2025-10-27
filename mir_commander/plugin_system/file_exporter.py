from abc import ABC, abstractmethod
from pathlib import Path

from mir_commander.core.models import Item


class ExportFileError(Exception):
    pass


class FileExporter(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_extensions(self) -> list[str]: ...

    @abstractmethod
    def can_export_nested(self) -> bool: ...

    @abstractmethod
    def write(self, item: Item, path: Path, nested: bool): ...
