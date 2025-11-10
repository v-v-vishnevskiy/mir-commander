from pydantic import Field

from .base_data_structure import BaseDataStructure


class Molecule(BaseDataStructure):
    n_atoms: int = 0
    atomic_num: list[int] = []
    charge: int = 0
    multiplicity: int = 1
    contribution: float = Field(default=0.0, description="Contribution in mixtures in fraction of unit [0, 1]")
