from pathlib import Path

import numpy as np

from mir_commander import consts
from mir_commander.data_structures.molecule import Molecule, AtomicCoordinates
from mir_commander.ui.utils import item

from .utils import ItemParametrized


def load_cfour(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from Cfour log file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items: list[dict] = []
    messages: list[str] = []

    messages.append("Cfour format.")

    moldata = Molecule()
    molitem = item.Molecule(path.parts[1], moldata)
    molitem.file_path = path

    flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

    cart_set_number = 0

    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if "Z-matrix   Atomic            Coordinates (in bohr)" in line:
                cart_set_number += 1
                # Skip header of the table (2 lines)
                for block_line_number, block_line in enumerate(input_file):
                    if block_line_number > 0:
                        break

                # Read the table
                atomic_num = []
                at_coord_x = []
                at_coord_y = []
                at_coord_z = []
                for block_line in input_file:
                    if "--" in block_line:
                        break
                    line_items = block_line.split()
                    if line_items[1] == "0":
                        atomic_num.append(-1)
                    else:
                        atomic_num.append(int(line_items[1]))
                    at_coord_x.append(float(line_items[2]) * consts.BOHR2ANGSTROM)
                    at_coord_y.append(float(line_items[3]) * consts.BOHR2ANGSTROM)
                    at_coord_z.append(float(line_items[4]) * consts.BOHR2ANGSTROM)

                # Add the set of Cartesian coordinates directly to the molecule
                at_coord_data = AtomicCoordinates(
                    np.array(atomic_num, dtype="int16"),
                    np.array(at_coord_x, dtype="float64"),
                    np.array(at_coord_y, dtype="float64"),
                    np.array(at_coord_z, dtype="float64"),
                )
                at_coord_item = item.AtomicCoordinates(f"Set#{cart_set_number}", at_coord_data)
                molitem.appendRow(at_coord_item)

    # Autoview last set of coordinates
    if at_coord_item:
        flagged_items.append({"itempar": ItemParametrized(at_coord_item, {"maximize": True}), "view": True})

    return molitem, flagged_items, messages
