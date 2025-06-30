import re
from collections import defaultdict
from pathlib import Path

from ..models import AtomicCoordinates, Item, Molecule, Unex
from .consts import babushka_priehala


version_validator = re.compile(r"^([0-9]+).([0-9]+)-([0-9]+)-([a-z0-9]+)$")  # For example 1.7-33-g5a83887


def is_unex(lines: list[str]) -> bool:
    return lines[0].strip().startswith("UNEX") and version_validator.match(lines[0].split()[1])


def load_unex(path: Path, logs: list) -> Item:
    """
    Import data from UNEX file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """

    result = Item(name=path.name, data=Unex(), metadata={"type": "unex"})

    molecules: dict[str, Item] = {}
    mol_cart_set_number: dict[str, int] = defaultdict(int)  # name: number of sets of Cartesian coordinates
    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if line_number == 0:
                logs.append(line.strip())  # First string is the UNEX version.
            if "> Cartesian coordinates of all atoms (Angstroms) in" in line:
                molecule_name = line.split(">")[0]
                if molecule_name in molecules:
                    molecule = molecules[molecule_name]
                else:
                    molecule = Item(name=molecule_name, data=Molecule())
                    molecules[molecule_name] = molecule
                    result.items.append(molecule)

                mol_cart_set_number[molecule_name] += 1

                # Skip header of the table (3 lines)
                for block_line_number, block_line in enumerate(input_file):
                    if block_line_number > 1:
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
                    atomic_num.append(int(line_items[2]))
                    atom_coord_x.append(float(line_items[4]))
                    atom_coord_y.append(float(line_items[5]))
                    atom_coord_z.append(float(line_items[6]))

                # Add the set of Cartesian coordinates directly to the molecule
                at_coord_data = Item(
                    name=f"Set#{mol_cart_set_number[molecule_name]}",
                    data=AtomicCoordinates(
                        atomic_num=atomic_num, 
                        x=atom_coord_x, 
                        y=atom_coord_y, 
                        z=atom_coord_z,
                    ),
                )
                molecule.items.append(at_coord_data)
    
    for item in result.items:
        if item.items:
            item.items[-1].metadata[babushka_priehala] = True

    return result
