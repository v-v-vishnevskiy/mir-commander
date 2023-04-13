from mir_commander.projects.base import Project


class Molecule(Project):
    """The class of projects with molecules.

    Instances of this class are for collecting of molecules.
    """

    def __init__(self, title: str):
        super().__init__(title)
