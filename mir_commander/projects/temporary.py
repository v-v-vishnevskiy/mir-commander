from pathlib import Path

from mir_commander.projects.base import Project
from mir_commander.utils.config import Config


class Temporary(Project):
    def __init__(self, path: Path):
        super().__init__(path, Config())

    @property
    def is_temporary(self) -> bool:
        return True
