import os

from mir_commander.projects.base import Project
from mir_commander.utils.config import Config


class Temporary(Project):
    def __init__(self, path: str = ""):
        splitted_path = os.path.split(path)
        super().__init__(os.path.abspath(splitted_path[0]), Config(""))
        self._name = splitted_path[1]

    @property
    def name(self) -> str:
        return self.settings["name"] or self._name

    @property
    def is_temporary(self) -> bool:
        return True
