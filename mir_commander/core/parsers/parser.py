from pathlib import Path

from ..models import Item
from .cclib_parser import load_cclib
from .cfour_parser import is_cfour, load_cfour
from .mdlmol2000_parser import is_mdlmol2000, load_mdlmol2000
from .unex_parser import is_unex, load_unex
from .xyz_parser import is_xyz, load_xyz
from .gaucube_parser import is_gaucube, load_gaucube


def load_file(path: Path, logs: list[str]) -> Item:
    lines = []
    line_number_limit = 100
    with path.open("r") as input_file:
        for i, line in enumerate(input_file):
            lines.append(line)
            if i >= line_number_limit:
                break

    if (ver := is_unex(lines)) != 0:
        return load_unex(ver, path, logs)
    elif is_xyz(lines):
        return load_xyz(path, logs)
    elif is_cfour(lines):
        return load_cfour(path, logs)
    elif is_mdlmol2000(lines):
        return load_mdlmol2000(path, logs)
    elif is_gaucube(path):
        return load_gaucube(path, logs)
    else:
        return load_cclib(path, logs)
