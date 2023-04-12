from dataclasses import dataclass


@dataclass
class Molecule:
    """Class of molecules.

    Contains list of atoms.
    """

    atnum: list[int]  # Atomic numbers
    atccx: list[float]  # Cartesian coordinates X [A]
    atccy: list[float]  # Cartesian coordinates Y [A]
    atccz: list[float]  # Cartesian coordinates Z [A]
