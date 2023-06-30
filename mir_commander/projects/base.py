import os
from typing import TYPE_CHECKING

from PySide6.QtGui import QStandardItem, QStandardItemModel

from mir_commander.utils.config import Config
from mir_commander.utils.settings import Settings

if TYPE_CHECKING:
    from mir_commander.ui.utils.item import Item


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
    def items_marked_to_view(self) -> list["Item"]:
        """
        Returns list of items marked as opened
        """
        result = []
        for item in self.config["items.marked_to_view"] or []:
            if item := self._item(item.split("."), self.root_item):
                result.append(item)
        return result

    @property
    def items_marked_to_expand(self) -> list["Item"]:
        """
        Returns list of items marked as expanded
        """
        result = []
        for item in self.config["items.marked_to_expand"] or []:
            if item := self._item(item.split("."), self.root_item):
                result.append(item)
        return result

    def mark_item_to_view(self, item: "Item"):
        opened = self.config["items.marked_to_view"] or []
        path = item.path
        if path not in opened:
            opened.append(path)
        self.config["items.marked_to_view"] = opened

    def mark_item_to_expand(self, item: "Item"):
        expanded = self.config["items.marked_to_expand"] or []
        path = item.path
        if path not in expanded:
            expanded.append(path)
        self.config["items.marked_to_expand"] = expanded

    def _item(self, path: list[str], parent: QStandardItem) -> None | QStandardItem:
        try:
            row = int(path.pop(0))
        except ValueError:
            return None

        if row < 0 or row >= parent.rowCount():
            return None

        item = parent.child(row)
        if path:
            return self._item(path, item)
        else:
            return item
