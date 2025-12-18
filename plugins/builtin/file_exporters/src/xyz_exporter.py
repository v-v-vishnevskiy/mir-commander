from pathlib import Path
from typing import Any

from mir_commander.api.data_structures.atomic_coordinates import AtomicCoordinates
from mir_commander.api.file_exporter import ExportFileError
from mir_commander.api.project_node_schema import ProjectNodeSchema
from mir_commander.core.chemistry import atomic_number_to_symbol


def write(node: ProjectNodeSchema, path: Path, format_params: dict[str, Any]):
    if not isinstance(node.data, AtomicCoordinates):
        raise ExportFileError("Invalid node data")

    title = format_params.get("title", node.name)
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
