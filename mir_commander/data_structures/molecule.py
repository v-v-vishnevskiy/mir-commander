from dataclasses import dataclass, field

import numpy as np

from mir_commander.data_structures.base import DataStructure


@dataclass
class AtomicCoordinates(DataStructure):
    """Class of atomic positions defined as Cartesian coordinates.

    We need this separately because a molecule may have multiple sets of
    geometries, for example as a result of optimization,
    (multidimensional) scans, IRC scans, etc.
    Thus, the basic properties of atoms, common for all possible geometries,
    are collected in the Molecule instance and only the different sets of
    geometries are in separate instances of AtomicCoordinates.
    Note, in a similar manner we may design a class for Z-matrices, etc.
    """

    x: np.ndarray = field(default_factory=lambda: np.empty(0, dtype="float64"))  # Cartesian coordinates X [A]
    y: np.ndarray = field(default_factory=lambda: np.empty(0, dtype="float64"))  # Cartesian coordinates Y [A]
    z: np.ndarray = field(default_factory=lambda: np.empty(0, dtype="float64"))  # Cartesian coordinates Z [A]


@dataclass
class Molecule(DataStructure):
    """Class of molecules."""

    natoms: int = 0  # Number of atoms
    atomic_num: np.ndarray = field(default_factory=lambda: np.empty(0, dtype="int16"))  # Atomic numbers
    charge: int = 0
    multiplicity: int = 1
