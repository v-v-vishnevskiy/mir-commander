from dataclasses import dataclass

from mir_commander.api.program import NodeChangedAction


@dataclass
class AtomicCoordinatesAddAtomAction(NodeChangedAction): ...


@dataclass
class AtomicCoordinatesNewSymbolAction(NodeChangedAction):
    atom_index: int


@dataclass
class AtomicCoordinatesNewPositionAction(NodeChangedAction):
    atom_index: int


@dataclass
class AtomicCoordinatesRemoveAtomsAction(NodeChangedAction):
    atom_indices: list[int]


@dataclass
class AtomicCoordinatesSwapAtomsIndicesAction(NodeChangedAction):
    atom_index_1: int
    atom_index_2: int
