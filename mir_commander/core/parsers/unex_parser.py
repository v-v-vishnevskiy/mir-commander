import logging
import re
from collections import defaultdict
from enum import Enum
from pathlib import Path

from periodictable import elements

from ..errors import LoadFileError
from ..models import AtomicCoordinates, Item, Molecule, Unex
from .consts import babushka_priehala

logger = logging.getLogger("Parsers.UnexParser")
version_validator = re.compile(r"^([0-9]+).([0-9]+)-([0-9]+)-([a-z0-9]+)$")  # For example 1.7-33-g5a83887


class Unex2XyzFormat(Enum):
    INVALID = 0
    UNEX = 1
    MOL = 2


def is_unex(lines: list[str]) -> int:
    """
    Returns UNEX version number encoded in a single integer number
    or zero if not a UNEX-specific string.
    """
    if lines[0].strip().startswith("UNEX"):
        re_result = version_validator.match(lines[0].split()[1])
        if re_result is not None:
            groups = re_result.groups()
            return 1000000 * int(groups[0]) + 10000 * int(groups[1]) + int(groups[2])
        else:
            return 0
    else:
        return 0


def load_unex(version: int, path: Path, logs: list) -> Item:
    """
    Import data from UNEX file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    logger.info("Parsing UNEX file ...")

    result = Item(name=path.name, data=Unex(), metadata={"type": "unex"})

    # UNEX 1.x
    if version < 2000000:
        result = load_unex1x(path, logs)
    # UNEX >= 2.x
    else:
        result = load_unex2x(path, logs)

    # Currently it is assumed that top-level items are molecules
    for item in result.items:
        # Currently it is assumed that molecules may contain only sets of Cartesian coordinates
        if item.items:
            item.items[-1].metadata[babushka_priehala] = True

    return result


def load_unex1x(path: Path, logs: list) -> Item:
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

    return result


def load_unex2x(path: Path, logs: list) -> Item:
    result = Item(name=path.name, data=Unex(), metadata={"type": "unex"})

    molecules: dict[str, Item] = {}
    mol_cart_set_number: dict[str, int] = defaultdict(int)  # name: number of sets of Cartesian coordinates

    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if line_number == 0:
                logs.append(line.strip())  # First string is the UNEX version.

            if "Cartesian coordinates (Angstroms) of atoms in" in line:
                molecule_name = line.split(" ")[6].strip()
                if molecule_name in molecules:
                    molecule = molecules[molecule_name]
                else:
                    molecule = Item(name=molecule_name, data=Molecule())
                    molecules[molecule_name] = molecule
                    result.items.append(molecule)

                mol_cart_set_number[molecule_name] += 1

                xyz_format = Unex2XyzFormat.INVALID
                delimeter_number = 0
                # Read header to determine format
                for block_line_number, block_line in enumerate(input_file):
                    if "Format:" in block_line:
                        format_str = block_line.split(" ")[1].strip()
                        if format_str == "UNEX":
                            xyz_format = Unex2XyzFormat.UNEX
                        elif format_str == "MOL":
                            xyz_format = Unex2XyzFormat.MOL
                        else:
                            logger.error("Invalid or unknown XYZ format: %s", format_str)
                            raise LoadFileError(f"Invalid or unknown XYZ format {format_str}")
                    elif "--" in block_line:
                        if xyz_format == Unex2XyzFormat.UNEX:
                            delimeter_number += 1
                            if delimeter_number == 2:
                                break
                        else:
                            break

                if xyz_format == Unex2XyzFormat.MOL:
                    # Skip header of the MOL format (2 lines)
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

                    if xyz_format == Unex2XyzFormat.UNEX:
                        line_items = block_line.split()
                        atomic_num.append(int(line_items[2]))
                        atom_coord_x.append(float(line_items[4]))
                        atom_coord_y.append(float(line_items[5]))
                        atom_coord_z.append(float(line_items[6]))
                    elif xyz_format == Unex2XyzFormat.MOL:
                        line_items = block_line.split()

                        try:
                            # Convert here atomic symbol to atomic number
                            if line_items[0] == "X":
                                at_num = -1
                            else:
                                at_num = elements.symbol(line_items[0]).number
                        except ValueError:
                            logger.error("Invalid atom symbol: %s", line_items[0])
                            raise LoadFileError(f"Invalid atom symbol {line_items[0]}")

                        atomic_num.append(at_num)
                        atom_coord_x.append(float(line_items[1]))
                        atom_coord_y.append(float(line_items[2]))
                        atom_coord_z.append(float(line_items[3]))

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

    return result
