import os

from mir_commander.settings import Settings
from mir_commander.utils.items_model import ItemsModel


class Project:
    """The most basic class of projects."""

    def __init__(self, path: str):
        self.path = os.path.normpath(path)
        self.settings = Settings(os.path.join(self.path, ".mircmd", "config"))
        self.items = ItemsModel("")

    @property
    def title(self) -> str:
        return os.path.split(self.path)[1] or "/"
