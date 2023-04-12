from mir_commander.data_structures.molecule import Molecule as MolObject
from mir_commander.projects.base import Project


class Molecule(Project):
    """The class of projects with molecules.

    Instances of this class are for collecting of molecules.
    """

    def __init__(self):
        self.molecules = []

    def add_molecule(self, mol: MolObject):
        self.molecules.append(mol)
