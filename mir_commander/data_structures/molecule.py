from dataclasses import dataclass, field
from typing import List

from mir_commander.data_structures.base import DataStructure


@dataclass
class Molecule(DataStructure):
    """Class of molecules.

    Contains: list of atoms, list of child molecules-isotopolgues.
    """

    atomic_num: List[int]  # Atomic numbers
    atom_cx: List[float]  # Cartesian coordinates X [A]
    atom_cy: List[float]  # Cartesian coordinates Y [A]
    atom_cz: List[float]  # Cartesian coordinates Z [A]
    isotop_mol: List["Molecule"] = field(default_factory=list)  # List of isotopologues
