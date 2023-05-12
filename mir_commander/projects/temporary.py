from mir_commander.projects.base import Project
from mir_commander.utils.config import Config


class Temporary(Project):
    def __init__(self, name: str = ""):
        super().__init__("", Config(""))
        self._name = name

    @property
    def name(self) -> str:
        return self._name
