from abc import ABC, abstractmethod
from pathlib import Path

from .project_node import ProjectNodeSchema


class ImportFileError(Exception):
    pass


class FileImporterPlugin(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_extensions(self) -> list[str]: ...

    @abstractmethod
    def read(self, path: Path, logs: list) -> ProjectNodeSchema: ...
