from pathlib import Path

from mir_commander.core.parsers import load_file

from .config import ProjectConfig
from .models import Data, Item


class Project:
    def __init__(self, path: Path = Path(), temporary: bool = False):
        self.path = path
        self._is_temporary = temporary
        self.data = Data.load(path / "data.yaml")
        self.config = ProjectConfig.load(path / "config.yaml")

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_temporary(self) -> bool:
        return self._is_temporary

    def import_file(self, file_path: Path, logs: list[str]) -> Item:
        imported_item = load_file(file_path, logs)
        self.data.items.append(imported_item)
        self.save()
        return imported_item

    def save(self):
        if not self.is_temporary:
            self.data.dump()
            self.config.dump()
