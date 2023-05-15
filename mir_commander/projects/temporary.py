from mir_commander.projects.base import Project
from mir_commander.utils.config import Config


class Temporary(Project):
    def __init__(self, name: str = ""):
        super().__init__("", Config(""))
        self._name = name

    @property
    def name(self) -> str:
        return self.settings["name"] or self._name

    @property
    def is_temporary(self) -> bool:
        return True
