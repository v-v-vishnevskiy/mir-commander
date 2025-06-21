from collections import defaultdict
from pathlib import Path

import numpy as np

from mir_commander.data_structures.molecule import AtomicCoordinates
from mir_commander.data_structures import unex
from mir_commander.ui.utils import item

from .utils import ItemParametrized


def load_unex(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from UNEX file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items: list[dict] = []
    messages: list[str] = []
    mol_items: dict[str, item.Molecule] = {}  # name: item
    mol_cart_item_last: dict[str, item.AtomicCoordinates] = {}  # name of molecule: last item of Cartesian coordinates
    mol_cart_set_number: dict[str, int] = defaultdict(int)  # name: number of sets of Cartesian coordinates

    project_data = unex.Project()
    rootitem = item.UnexProject(path.parts[-1], project_data)
    rootitem.file_path = path

    flagged_items.append({"itempar": ItemParametrized(rootitem, {}), "expand": True})

    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if line_number == 0:
                messages.append(line.strip())  # First string is the UNEX version.
            if "> Cartesian coordinates of all atoms (Angstroms) in" in line:
                molname = line.split(">")[0]
                if molname in mol_items:
                    current_mol_item = mol_items[molname]
                else:
                    current_mol_ds = unex.Molecule()
                    current_mol_item = item.Molecule(molname, current_mol_ds)
                    mol_items[molname] = current_mol_item
                    rootitem.appendRow(current_mol_item)

                mol_cart_set_number[molname] += 1

                # Skip header of the table (3 lines)
                for block_line_number, block_line in enumerate(input_file):
                    if block_line_number > 1:
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
                    atomic_num.append(int(line_items[2]))
                    at_coord_x.append(float(line_items[4]))
                    at_coord_y.append(float(line_items[5]))
                    at_coord_z.append(float(line_items[6]))

                # Add the set of Cartesian coordinates directly to the molecule
                at_coord_data = AtomicCoordinates(
                    np.array(atomic_num, dtype="int16"),
                    np.array(at_coord_x, dtype="float64"),
                    np.array(at_coord_y, dtype="float64"),
                    np.array(at_coord_z, dtype="float64"),
                )
                at_coord_item = item.AtomicCoordinates(f"Set#{mol_cart_set_number[molname]}", at_coord_data)
                current_mol_item.appendRow(at_coord_item)
                mol_cart_item_last[molname] = at_coord_item

    # Set flags to items
    prm = {}
    if len(mol_cart_item_last) == 1:
        prm = {"maximize": True}

    # Autoview last sets of coordinates of each molecule
    for at_coord_item in mol_cart_item_last.values():
        flagged_items.append({"itempar": ItemParametrized(at_coord_item, prm), "view": True})

    return rootitem, flagged_items, messages
