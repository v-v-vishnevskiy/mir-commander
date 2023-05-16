import os
from typing import TYPE_CHECKING, List, Union

from PySide6.QtGui import QStandardItem, QStandardItemModel

from mir_commander.utils.config import Config
from mir_commander.utils.settings import Settings

if TYPE_CHECKING:
    from mir_commander.utils.item import Item


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

    @property
    def opened_items(self) -> List["Item"]:
        """
        Returns list of items marked as opened
        """
        result = []
        for item in self.config["opened"] or []:
            if item := self._item(item.split("/"), self.root_item):
                result.append(item)
        return result

    def mark_item_as_opened(self, item: "Item"):
        opened = self.config["opened"] or []
        path = item.path
        if path not in opened:
            opened.append(path)
        self.config["opened"] = opened

    def _item(self, path: List[str], parent: QStandardItem) -> Union[None, QStandardItem]:
        part = path.pop(0).replace("~1", "/").replace("~0", "~")
        for i in range(parent.rowCount()):
            item = parent.child(i)
            if item.text() == part:
                if path:
                    return self._item(path, item)
                else:
                    return item
        return None
