from pathlib import Path

from .config import ProjectConfig
from .models import Data


class Project:
    def __init__(self, path: None | Path = None):
        self.path = path
        self.data = Data.load(path / "data.yaml") if path else Data()
        self.config = ProjectConfig.load(path / "config.yaml") if path else ProjectConfig()

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_temporary(self) -> bool:
        return self.path is None

    def save(self):
        self.data.dump()
        self.config.dump()
