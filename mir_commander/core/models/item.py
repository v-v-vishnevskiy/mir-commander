from typing import Annotated, Any, Self

from pydantic import BaseModel, Field, field_validator

from .molecule import AtomicCoordinates, AtomicCoordinatesGroup, Molecule
from .unex import Unex
from .volcube import VolCube

ItemData = Annotated[
    VolCube | AtomicCoordinates | AtomicCoordinatesGroup | Molecule | Unex, Field(discriminator="data_type")
]


class Item(BaseModel):
    name: str
    data: None | ItemData = None
    items: list[Self] = []
    metadata: dict[str, Any] = {}

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()
