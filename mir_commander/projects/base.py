import os

from mir_commander.settings import Settings
from mir_commander.utils.config import Config
from mir_commander.utils.item import Item


class Project:
    """The most basic class of projects."""

    def __init__(self, path: str):
        self.path = os.path.normpath(path)
        self.config = Config(os.path.join(self.path, ".mircmd", "config.yaml"))
        self.settings = Settings(self.config)
        self.root_item = Item("root")

    @property
    def name(self) -> str:
        return self.settings["name"] or os.path.split(self.path)[1] or "/"
