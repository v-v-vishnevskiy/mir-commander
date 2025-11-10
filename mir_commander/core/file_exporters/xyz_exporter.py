from pathlib import Path
from typing import Any

from mir_commander.api.data_structures.atomic_coordinates import AtomicCoordinates
from mir_commander.api.file_exporter import ExportFileError
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1
from mir_commander.utils.chem import atomic_number_to_symbol

from .utils import BaseExporter


class XYZExporter(BaseExporter):
    def get_name(self) -> str:
        return "XYZ"

    def get_supported_node_types(self) -> list[str]:
        return ["atomic_coordinates"]

    def get_settings_config(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "title",
                "label": "Title",
                "type": "text",
                "default": {"type": "property", "value": "node.full_name"},
                "required": False,
            }
        ]

    def get_extensions(self) -> list[str]:
        return ["xyz"]

    def write(self, node: ProjectNodeSchemaV1, path: Path, format_settings: dict[str, Any]):
        if node.type not in self.get_supported_node_types():
            raise ExportFileError(f"Node type {node.type} is not supported")

        if not isinstance(node.data, AtomicCoordinates):
            raise ExportFileError("Invalid node data")

        title = format_settings.get("title", node.name)
        atomic_num: list[int] = node.data.atomic_num
        x: list[float] = node.data.x
        y: list[float] = node.data.y
        z: list[float] = node.data.z

        n = len(atomic_num)
        with open(path, "w") as f:
            f.write(f"{n}\n")
            f.write(f"{title}\n")
            for i in range(n):
                symbol = atomic_number_to_symbol(atomic_num[i])
                f.write(f"{symbol:<6} {x[i]:>20.14f} {y[i]:>20.14f} {z[i]:>20.14f}\n")
