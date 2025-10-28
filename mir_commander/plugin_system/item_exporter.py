from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from mir_commander.core.models import Item


class ExportItemError(Exception):
    pass


class ItemExporter(ABC):
    @abstractmethod
    def get_name(self) -> str: ...

    @abstractmethod
    def get_extensions(self) -> list[str]: ...

    @abstractmethod
    def get_settings_config(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def write(self, item: Item, path: Path, format_settings: dict[str, Any]): ...

    # TODO: add protection for modifying item data. Item must be immutable.
