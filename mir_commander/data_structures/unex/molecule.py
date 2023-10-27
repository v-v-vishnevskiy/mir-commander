from dataclasses import dataclass

from mir_commander.data_structures.molecule import Molecule as GenericMolecule


@dataclass
class Molecule(GenericMolecule):
    """Class of molecules in UNEX projects."""

    contribution: float = 0.0  # Contribution in mixtures in fraction of unit [0, 1]
