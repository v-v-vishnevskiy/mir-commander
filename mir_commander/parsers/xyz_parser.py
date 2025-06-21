import logging
from enum import Enum
from pathlib import Path

import numpy as np
from periodictable import elements

from mir_commander.data_structures.molecule import Molecule, AtomicCoordinates
from mir_commander.ui.utils import item

from .utils import ItemParametrized

logger = logging.getLogger(__name__)


class XyzParserState(Enum):
    INIT = 0
    COMMENT = 1
    CARDS = 2


def load_xyz(path: Path) -> tuple[item.Item, list[dict], list[str]]:
    """
    Import data from XYZ file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    flagged_items: list[dict] = []
    messages: list[str] = []

    messages.append("XYZ format.")

    moldata = Molecule()
    molitem = item.Molecule(path.parts[-1], moldata)
    molitem.file_path = path

    flagged_items.append({"itempar": ItemParametrized(molitem, {}), "expand": True})

    state = XyzParserState.INIT
    at_coord_item = None
    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if state == XyzParserState.INIT:
                if len(line.strip()) == 0:
                    # Silently exit the cycle early if empty line is found where number of atoms can be expected.
                    # This may happen, for example, in case of empty line after the last set of Cartesian coordinates.
                    break
                try:
                    num_atoms = int(line.strip())
                except ValueError:
                    logger.info(f"Invalid line {line_number+1}, expected number of atoms.")
                    raise
                if num_atoms <= 0:
                    raise ValueError(f"Invalid number of atoms {num_atoms} at line {line_number+1}.")
                state = XyzParserState.COMMENT
            elif state == XyzParserState.COMMENT:
                title = line.strip()
                if len(title) == 0:
                    title = f"Set@line={line_number}"
                state = XyzParserState.CARDS
                num_read_cards = 0
                atom_atomic_num = []
                atom_coord_x = []
                atom_coord_y = []
                atom_coord_z = []
            elif state == XyzParserState.CARDS:
                line_items = line.strip().split()
                try:
                    atomic_num = int(line_items[0])
                except ValueError:
                    try:
                        # Convert here atomic symbol to atomic number
                        if line_items[0] == "X":
                            atomic_num = -1
                        elif line_items[0] == "Q":
                            atomic_num = -2
                        else:
                            atomic_num = elements.symbol(line_items[0]).number
                    except ValueError:
                        logger.info(f"Invalid atom at line {line_number + 1}.")
                        raise
                try:
                    coord_x = float(line_items[1])
                    coord_y = float(line_items[2])
                    coord_z = float(line_items[3])
                except ValueError:
                    # Something is wrong with format
                    logger.info(f"Invalid coordinate value(s) at line {line_number + 1}.")
                    raise

                num_read_cards += 1
                atom_atomic_num.append(atomic_num)
                atom_coord_x.append(coord_x)
                atom_coord_y.append(coord_y)
                atom_coord_z.append(coord_z)

                if num_read_cards == num_atoms:
                    # Add the set of Cartesian coordinates directly to the molecule
                    at_coord_data = AtomicCoordinates(
                        np.array(atom_atomic_num, dtype="int16"),
                        np.array(atom_coord_x, dtype="float64"),
                        np.array(atom_coord_y, dtype="float64"),
                        np.array(atom_coord_z, dtype="float64"),
                    )
                    at_coord_item = item.AtomicCoordinates(title, at_coord_data)
                    molitem.appendRow(at_coord_item)

                    state = XyzParserState.INIT

    # Autoview last set of coordinates
    if at_coord_item:
        flagged_items.append({"itempar": ItemParametrized(at_coord_item, {"maximize": True}), "view": True})

    return molitem, flagged_items, messages
