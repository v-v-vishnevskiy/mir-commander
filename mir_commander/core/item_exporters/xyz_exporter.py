from pathlib import Path
from typing import Any

from mir_commander.plugin_system.item_exporter import ExportItemError, ItemExporter
from mir_commander.utils.chem import atomic_number_to_symbol

from ..models import Item
from ..models.molecule import AtomicCoordinates


class XYZExporter(ItemExporter):
    def get_name(self) -> str:
        return "XYZ"

    def get_settings_config(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "title",
                "label": "Title",
                "type": "text",
                "default": {"type": "property", "value": "item.name"},
                "required": False,
            }
        ]

    def get_extensions(self) -> list[str]:
        return ["xyz"]

    def write(self, item: Item, path: Path, format_settings: dict[str, Any]):
        title = format_settings.get("title", item.name)
        if isinstance(item.data, AtomicCoordinates):
            n = len(item.data.atomic_num)
            with open(path, "w") as f:
                f.write(f"{n}\n")
                f.write(f"{title}\n")
                for i in range(n):
                    symbol = atomic_number_to_symbol(item.data.atomic_num[i])
                    x = item.data.x[i]
                    y = item.data.y[i]
                    z = item.data.z[i]
                    f.write(f"{symbol:<6} {x:>20.14f} {y:>20.14f} {z:>20.14f}\n")
        else:
            raise ExportItemError("Only atomic coordinates are supported")
