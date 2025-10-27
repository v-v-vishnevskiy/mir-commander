from pathlib import Path

from mir_commander.plugin_system.file_exporter import FileExporter

from ..models import Item


class XYZExporter(FileExporter):
    def get_name(self) -> str:
        return "XYZ"

    def can_export_nested(self) -> bool:
        return True

    def get_extensions(self) -> list[str]:
        return ["xyz"]

    def write(self, item: Item, path: Path, nested: bool):
        pass
