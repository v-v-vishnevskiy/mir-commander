from dataclasses import dataclass
from typing import List

from mir_commander.data_structures.base import DataStructure


@dataclass
class Geometry(DataStructure):
    """Class of molecular geometry.

    Contains atomic numbers and Cartesian coordinates of atoms.
    """

    atomic_num: List[int]  # Atomic numbers
    atoms_cx: List[float]  # Cartesian coordinates X [A]
    atoms_cy: List[float]  # Cartesian coordinates Y [A]
    atoms_cz: List[float]  # Cartesian coordinates Z [A]


@dataclass
class Molecule(DataStructure):
    """Class of molecules."""
