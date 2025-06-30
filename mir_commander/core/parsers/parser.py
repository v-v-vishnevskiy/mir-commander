from pathlib import Path

from ..models import Item
from .cclib_parser import load_cclib
from .cfour_parser import is_cfour, load_cfour
from .mdlmol2000_parser import is_mdlmol2000, load_mdlmol2000
from .unex_parser import is_unex, load_unex
from .xyz_parser import is_xyz, load_xyz


def load_file(path: Path, logs: list[str]) -> Item:
    lines = []
    line_number_limit = 10
    with path.open("r") as input_file:
        for i, line in enumerate(input_file):
            lines.append(line)
            if i >= line_number_limit:
                break

    if is_unex(lines):
        return load_unex(path, logs)
    if is_xyz(lines):
        return load_xyz(path, logs)
    if is_cfour(lines):
        return load_cfour(path, logs)
    if is_mdlmol2000(lines):
        return load_mdlmol2000(path, logs)
    return load_cclib(path, logs)
