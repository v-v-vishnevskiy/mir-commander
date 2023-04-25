import os

from mir_commander.settings import Settings
from mir_commander.utils.item import Item


class Project:
    """The most basic class of projects."""

    def __init__(self, path: str):
        self.path = os.path.normpath(path)
        self.settings = Settings(os.path.join(self.path, ".mircmd", "config"))
        self.root_item = Item("root")

    @property
    def title(self) -> str:
        return os.path.split(self.path)[1] or "/"
