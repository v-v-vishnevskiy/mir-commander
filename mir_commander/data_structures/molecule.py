from dataclasses import dataclass, field
from typing import List


@dataclass
class Molecule:
    """Class of molecules.

    Contains: list of atoms, list of child molecules-isotopolgues.
    """

    atnum: List[int]  # Atomic numbers
    atcoordx: List[float]  # Cartesian coordinates X [A]
    atcoordy: List[float]  # Cartesian coordinates Y [A]
    atcoordz: List[float]  # Cartesian coordinates Z [A]
    isotopmol: List["Molecule"] = field(default_factory=list)  # List of isotopologues
