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
