import logging
from pathlib import Path
from typing import Any

from .config import ProjectConfig
from .errors import LoadProjectError
from .file_manager import FileManager
from .models import Data, Item

logger = logging.getLogger("Core.Project")


class Project:
    def __init__(self, path: Path, file_manager: FileManager, temporary: bool = False):
        self.path = path
        self._file_manager = file_manager
        self._is_temporary = temporary
        self.data = Data.load(path / "data.yaml")
        self.config = ProjectConfig.load(path / "config.yaml")

        self._load_project()

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_temporary(self) -> bool:
        return self._is_temporary

    def _load_project(self):
        if self.is_temporary:
            return

        logger.info("Loading project: %s", self.path)

        self.path = self.path.resolve()
        if self.path.is_file():
            raise LoadProjectError(f"Invalid path: {self.path}")
        logger.info("Loading project completed")

    def import_files(self, files: list[Path], logs: list[str], parent: Item | None = None) -> list[Item]:
        items = []
        for file in files:
            try:
                items.append(self.import_file(file, logs, parent))
            except Exception as e:
                logs.append(f"Failed to import file {file}: {e}")
        return items

    def import_file(self, path: Path, logs: list[str], parent: Item | None = None) -> Item:
        imported_item = self._file_manager.import_file(path, logs)
        if parent is not None:
            parent.items.append(imported_item)
        else:
            self.data.items.append(imported_item)
        self.save()
        return imported_item

    def export_item(self, item: Item, exporter_name: str, path: Path, format_settings: dict[str, Any]):
        self._file_manager.export_item(
            item=item, exporter_name=exporter_name, path=path, format_settings=format_settings
        )

    def save(self):
        if not self.is_temporary:
            self.data.dump()
            self.config.dump()
