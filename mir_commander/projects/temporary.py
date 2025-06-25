from pathlib import Path

from .base import Project
from .config import Config


class Temporary(Project):
    def __init__(self, path: Path):
        super().__init__(path, Config(name=path.parts[-1]))

    @property
    def is_temporary(self) -> bool:
        return True
