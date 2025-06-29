import logging
import re
from enum import Enum
from pathlib import Path

from periodictable import elements

from ..errors import LoadFileError
from ..models import AtomicCoordinates, Item, Molecule

logger = logging.getLogger(__name__)

int_validator = re.compile(r"^[1-9][0-9]*$")  # For example 15
card_validator = re.compile(
    r"^([A-Z][a-z]?|[0-9]+)([\s]+[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?){3}$"  # For example Ca 1.0 -2.0 +0.1e-01
)

class ParserState(Enum):
    INIT = 0
    COMMENT = 1
    CARDS = 2


def is_xyz(lines: list[str]) -> bool:
    if numat_match := int_validator.match(lines[0].strip()):
        numat = int(numat_match.group(0))
    else:
        return False

    # in XYZ format second line is comment, it may be anything, even empty
    for line in lines[2:numat+2]:
        if not card_validator.match(line.strip()):
            return False

    return True


def load_xyz(path: Path, logs: list) -> Item:
    """
    Import data from XYZ file, build and populate a respective tree of items.
    Also return a list of flagged items.
    Additionally return a list of messages, which can be printed later.
    """
    logs.append("XYZ format.")

    result = Item(name=path.parts[-1], data=Molecule(), metadata={"type": "xyz"})

    state = ParserState.INIT
    at_coord_item = None
    with path.open("r") as input_file:
        for line_number, line in enumerate(input_file):
            if state == ParserState.INIT:
                if len(line.strip()) == 0:
                    # Silently exit the cycle early if empty line is found where number of atoms can be expected.
                    # This may happen, for example, in case of empty line after the last set of Cartesian coordinates.
                    break
                try:
                    num_atoms = int(line.strip())
                except ValueError:
                    logger.error("Invalid line %d, expected number of atoms.", line_number + 1)
                    raise LoadFileError()
                if num_atoms <= 0:
                    logger.error("Invalid number of atoms %d at line %d.", num_atoms, line_number + 1)
                    raise LoadFileError()
                state = ParserState.COMMENT
            elif state == ParserState.COMMENT:
                title = line.strip()
                if len(title) == 0:
                    title = f"Set@line={line_number}"
                state = ParserState.CARDS
                num_read_cards = 0
                atom_atomic_num = []
                atom_coord_x = []
                atom_coord_y = []
                atom_coord_z = []
            elif state == ParserState.CARDS:
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
                        logger.error("Invalid atom at line %d.", line_number + 1)
                        raise LoadFileError()
                try:
                    coord_x = float(line_items[1])
                    coord_y = float(line_items[2])
                    coord_z = float(line_items[3])
                except ValueError:
                    # Something is wrong with format
                    logger.error("Invalid coordinate value(s) at line %d.", line_number + 1)
                    raise LoadFileError()

                num_read_cards += 1
                atom_atomic_num.append(atomic_num)
                atom_coord_x.append(coord_x)
                atom_coord_y.append(coord_y)
                atom_coord_z.append(coord_z)

                if num_read_cards == num_atoms:
                    # Add the set of Cartesian coordinates directly to the molecule
                    at_coord_item = Item(
                        name=title,
                        data=AtomicCoordinates(
                            atomic_num=atom_atomic_num, 
                            x=atom_coord_x, 
                            y=atom_coord_y, 
                            z=atom_coord_z,
                        ),
                    )
                    result.items.append(at_coord_item)

                    state = ParserState.INIT

    return result
