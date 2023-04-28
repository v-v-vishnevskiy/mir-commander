import os

from mir_commander.utils.config import Config
from mir_commander.utils.item import Item
from mir_commander.utils.settings import Settings


class Project:
    """The most basic class of projects."""

    def __init__(self, path: str, config: Config):
        self.path = os.path.normpath(path)
        self.config = config
        self.settings = Settings(config)
        self.root_item = Item("root")

    @property
    def name(self) -> str:
        return self.settings["name"] or os.path.split(self.path)[1] or "/"
