from dataclasses import dataclass


@dataclass
class ItemChangedAction: ...


@dataclass
class AtomicCoordinatesAddAtomAction(ItemChangedAction): ...


@dataclass
class AtomicCoordinatesNewSymbolAction(ItemChangedAction):
    atom_index: int


@dataclass
class AtomicCoordinatesRemoveAtomsAction(ItemChangedAction):
    atom_indices: list[int]


@dataclass
class AtomicCoordinatesSwapAtomsIndicesAction(ItemChangedAction):
    atom_index_1: int
    atom_index_2: int
