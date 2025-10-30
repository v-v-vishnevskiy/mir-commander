from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .project_node import ProjectNodeSchema


class ExportFileError(Exception):
    pass


class FileExporterPlugin(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_extensions(self) -> list[str]: ...

    @abstractmethod
    def get_settings_config(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def write(self, node: ProjectNodeSchema, path: Path, format_settings: dict[str, Any]): ...
