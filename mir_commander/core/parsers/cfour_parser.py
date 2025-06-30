from pathlib import Path

from mir_commander import consts

from ..models import AtomicCoordinates, Item, Molecule
from .consts import babushka_priehala


def is_cfour(lines: list[str]) -> bool:
    for line in lines[1:]:
        if "<<<     CCCCCC     CCCCCC   |||     CCCCCC     CCCCCC   >>>" in line:
            return True
    return False


def load_cfour(path: Path, logs: list) -> Item:
    """
    Import data from Cfour log file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """

    logs.append("Cfour format.")

    result = Item(name=path.name, data=Molecule(), metadata={"type": "cfour"})

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
                atom_coord_x = []
                atom_coord_y = []
                atom_coord_z = []
                for block_line in input_file:
                    if "--" in block_line:
                        break
                    line_items = block_line.split()
                    if line_items[1] == "0":
                        atomic_num.append(-1)
                    else:
                        atomic_num.append(int(line_items[1]))
                    atom_coord_x.append(float(line_items[2]) * consts.BOHR2ANGSTROM)
                    atom_coord_y.append(float(line_items[3]) * consts.BOHR2ANGSTROM)
                    atom_coord_z.append(float(line_items[4]) * consts.BOHR2ANGSTROM)

                at_coord_item = Item(
                    name=f"Set#{cart_set_number}",
                    data=AtomicCoordinates(
                        atomic_num=atomic_num, 
                        x=atom_coord_x, 
                        y=atom_coord_y, 
                        z=atom_coord_z,
                    ),
                )
                result.items.append(at_coord_item)

    if result.items:
        result.items[-1].metadata[babushka_priehala] = True

    return result
