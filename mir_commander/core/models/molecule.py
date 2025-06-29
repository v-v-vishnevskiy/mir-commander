from typing import Literal

from pydantic import BaseModel, Field


class AtomicCoordinates(BaseModel):
    """
    Class of atomic positions defined as Cartesian coordinates.

    We need this separately because a molecule may have multiple sets of
    geometries, for example as a result of optimization,
    (multidimensional) scans, IRC scans, etc.
    Thus, the basic properties of atoms, common for all possible geometries,
    are collected in the Molecule instance and only the different sets of
    geometries are in separate instances of AtomicCoordinates.
    Note, in a similar manner we may design a class for Z-matrices, etc.
    """

    data_type: Literal["atomic_coordinates"] = "atomic_coordinates"

    atomic_num: list[int] = []
    x: list[float] = []  # Cartesian coordinates X [A]
    y: list[float] = []  # Cartesian coordinates Y [A]
    z: list[float] = []  # Cartesian coordinates Z [A]


class AtomicCoordinatesGroup(BaseModel):
    data_type: Literal["atomic_coordinates_group"] = "atomic_coordinates_group"


class Molecule(BaseModel):
    data_type: Literal["molecule"] = "molecule"

    n_atoms: int = 0
    atomic_num: list[int] = []
    charge: int = 0
    multiplicity: int = 1
    contribution: float = Field(default=0.0, description="Contribution in mixtures in fraction of unit [0, 1]")
