from dataclasses import dataclass, field
from typing import List

from mir_commander.data_structures.base import DataStructure
from mir_commander.data_structures.unex.molecule import Molecule


@dataclass
class Project(DataStructure):
    """Class of UNEX projects"""

    molecules: List[Molecule] = field(default_factory=lambda: [])
