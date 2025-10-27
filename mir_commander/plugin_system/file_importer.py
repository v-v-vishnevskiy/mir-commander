from abc import ABC, abstractmethod
from pathlib import Path

from mir_commander.core.models import Item


class ImportFileError(Exception):
    pass


class FileImporter(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_extensions(self) -> list[str]: ...

    @abstractmethod
    def read(self, path: Path, logs: list) -> Item: ...
