from dataclasses import dataclass


@dataclass
class ItemChangedAction: ...


@dataclass
class AtomicCoordinatesNewSymbolAction(ItemChangedAction):
    idx: int
    atomic_number: int


@dataclass
class AtomicCoordinatesRemoveAtomsAction(ItemChangedAction):
    indices: list[int]


@dataclass
class AtomicCoordinatesSwapAction(ItemChangedAction):
    index_1: int
    index_2: int
