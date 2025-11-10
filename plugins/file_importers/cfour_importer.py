from pathlib import Path

from mir_commander.api.data_structures.atomic_coordinates import AtomicCoordinates
from mir_commander.api.data_structures.molecule import Molecule
from mir_commander.api.file_importer import InvalidFormatError
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1 as Node
from mir_commander.utils import consts

from .utils import BaseImporter


class CFourImporter(BaseImporter):
    def _valudate(self, path: Path):
        lines = self.load_lines(path, 20)
        for line in lines[1:]:
            if "<<<     CCCCCC     CCCCCC   |||     CCCCCC     CCCCCC   >>>" in line:
                return
        raise InvalidFormatError()

    def get_name(self) -> str:
        return "CFOUR"

    def get_extensions(self) -> list[str]:
        return ["log"]

    def read(self, path: Path, logs: list[str]) -> Node:
        """
        Import data from Cfour log file, build and populate a respective tree of items.
        Also return a list of flagged items.
        Additionally return a list of messages, which can be printed later.
        """

        self._valudate(path)

        logs.append("Cfour format.")

        result = Node(name=path.name, data=Molecule(), type="molecule")

        cart_set_number = 0
        with path.open("r") as input_file:
            for _, line in enumerate[str](input_file):
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

                    at_coord_node = Node(
                        name=f"Set#{cart_set_number}",
                        type="atomic_coordinates",
                        data=AtomicCoordinates(atomic_num=atomic_num, x=atom_coord_x, y=atom_coord_y, z=atom_coord_z),
                    )
                    result.nodes.append(at_coord_node)

        # Mark the last imported coordinates for auto-opening
        if result.nodes:
            result.nodes[-1].auto_open = True

        return result
