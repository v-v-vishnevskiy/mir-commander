import os

from PySide6.QtGui import QStandardItem, QStandardItemModel

from mir_commander.utils.config import Config
from mir_commander.utils.settings import Settings


class Project:
    """The most basic class of projects."""

    def __init__(self, path: str, config: Config):
        self.path = os.path.normpath(path)
        self.config = config
        self.settings = Settings(config)
        self.model = QStandardItemModel()

    @property
    def name(self) -> str:
        return self.settings["name"] or os.path.split(self.path)[1] or "/"

    @property
    def root_item(self) -> QStandardItem:
        return self.model.invisibleRootItem()

    @property
    def is_temporary(self) -> bool:
        return False
