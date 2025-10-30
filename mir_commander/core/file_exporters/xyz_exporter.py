from pathlib import Path
from typing import Any

from mir_commander.plugin_system.file_exporter import ExportFileError, FileExporterPlugin
from mir_commander.plugin_system.project_node import ProjectNodeSchema
from mir_commander.utils.chem import atomic_number_to_symbol


class XYZExporter(FileExporterPlugin):
    def get_name(self) -> str:
        return "XYZ"

    def get_settings_config(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "title",
                "label": "Title",
                "type": "text",
                "default": {"type": "property", "value": "node.name"},
                "required": False,
            }
        ]

    def get_extensions(self) -> list[str]:
        return ["xyz"]

    def write(self, node: ProjectNodeSchema, path: Path, format_settings: dict[str, Any]):
        title = format_settings.get("title", node.name)
        if node.type == "atomic_coordinates":
            data = node.data
            n = len(data["atomic_num"])
            with open(path, "w") as f:
                f.write(f"{n}\n")
                f.write(f"{title}\n")
                for i in range(n):
                    symbol = atomic_number_to_symbol(data["atomic_num"][i])
                    x = data["x"][i]
                    y = data["y"][i]
                    z = data["z"][i]
                    f.write(f"{symbol:<6} {x:>20.14f} {y:>20.14f} {z:>20.14f}\n")
        else:
            raise ExportFileError("Only atomic coordinates are supported")
