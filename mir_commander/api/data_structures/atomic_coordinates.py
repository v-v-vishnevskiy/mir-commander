from ..program import NodeChangedAction
from .base_data_structure import BaseDataStructure


class AddAtomAction(NodeChangedAction): ...


class NewSymbolAction(NodeChangedAction):
    index: int


class NewPositionAction(NodeChangedAction):
    index: int


class RemoveAtomsAction(NodeChangedAction):
    indices: list[int]


class SwapAtomsIndicesAction(NodeChangedAction):
    index_1: int
    index_2: int


class AtomicCoordinates(BaseDataStructure):
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

    atomic_num: list[int] = []
    x: list[float] = []
    y: list[float] = []
    z: list[float] = []
