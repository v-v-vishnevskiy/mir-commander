import re
from enum import Enum
from pathlib import Path

from mir_commander.api.data_structures.atomic_coordinates import AtomicCoordinates
from mir_commander.api.data_structures.molecule import Molecule
from mir_commander.api.file_importer import ImportFileError, InvalidFormatError
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1 as Node
from mir_commander.utils.chem import symbol_to_atomic_number

from .utils import BaseImporter

card_validator = re.compile(
    r"^([A-Z][a-z]?|[0-9]+)([\s]+[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?){3}$"  # For example Ca 1.0 -2.0 +0.1e-01
)


class ParserState(Enum):
    INIT = 0
    COMMENT = 1
    CARDS = 2


class XYZImporter(BaseImporter):
    def _get_name(self) -> str:
        return "XYZ"

    def _get_version(self) -> tuple[int, int, int]:
        return (1, 0, 0)

    def _validate(self, path: Path):
        lines = self.load_lines(path, 10)

        try:
            numat = int(lines[0].strip())
        except ValueError:
            raise InvalidFormatError()

        # in XYZ format second line is comment, it may be anything, even empty
        for line in lines[2 : numat + 2]:
            if not card_validator.match(line.strip()):
                raise InvalidFormatError()

    def get_extensions(self) -> list[str]:
        return ["xyz"]

    def read(self, path: Path, logs: list[str]) -> Node:
        self._validate(path)

        logs.append("XYZ format.")

        result = Node(name=path.name, data=Molecule(), type="molecule")

        state = ParserState.INIT
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
                        raise ImportFileError(f"Invalid line {line_number + 1}, expected number of atoms.")
                    if num_atoms <= 0:
                        raise ImportFileError(f"Invalid number of atoms {num_atoms} at line {line_number + 1}.")
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
                                atomic_num = symbol_to_atomic_number(line_items[0])
                        except ValueError:
                            raise ImportFileError(f"Invalid atom at line {line_number + 1}.")
                    try:
                        coord_x = float(line_items[1])
                        coord_y = float(line_items[2])
                        coord_z = float(line_items[3])
                    except ValueError:
                        # Something is wrong with format
                        raise ImportFileError(f"Invalid coordinate value(s) at line {line_number + 1}.")

                    num_read_cards += 1
                    atom_atomic_num.append(atomic_num)
                    atom_coord_x.append(coord_x)
                    atom_coord_y.append(coord_y)
                    atom_coord_z.append(coord_z)

                    if num_read_cards == num_atoms:
                        # Add the set of Cartesian coordinates directly to the molecule
                        at_coord_item = Node(
                            name=title,
                            type="atomic_coordinates",
                            data=AtomicCoordinates(
                                atomic_num=atom_atomic_num,
                                x=atom_coord_x,
                                y=atom_coord_y,
                                z=atom_coord_z,
                            ),
                        )
                        result.nodes.append(at_coord_item)

                        state = ParserState.INIT

        # Mark the last imported coordinates for auto-opening
        if result.nodes:
            result.nodes[-1].auto_open = True

        return result
