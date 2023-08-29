import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtGui import QStandardItem, QStandardItemModel

from mir_commander.utils.config import Config
from mir_commander.utils.settings import Settings

if TYPE_CHECKING:
    from mir_commander.ui.utils.item import Item


@dataclass
class ItemParameters:
    item: "Item"
    parameters: dict


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

    def _get_items_from_config(self, category: str) -> list[ItemParameters]:
        result = []
        for item_dict in self.config[f"items.{category}"] or []:
            if item := self._item(item_dict["path"].split("."), self.root_item):
                result.append(ItemParameters(item, item_dict["parameters"]))
        return result

    @property
    def items_marked_to_view(self) -> list[ItemParameters]:
        """
        Returns list of items marked as (to be) opened in viewer(s)
        """
        return self._get_items_from_config("marked_to_view")

    @property
    def items_marked_to_expand(self) -> list[ItemParameters]:
        """
        Returns list of items marked as expanded
        """
        return self._get_items_from_config("marked_to_expand")

    def _add_item_to_config(self, item: "Item", category: str, parameters: dict):
        entries = self.config[f"items.{category}"] or []
        path = item.path
        if path not in entries:
            entries.append({"path": path, "parameters": parameters})
        self.config[f"items.{category}"] = entries

    def mark_item_to_view(self, item: "Item", parameters: dict):
        self._add_item_to_config(item, "marked_to_view", parameters)

    def mark_item_to_expand(self, item: "Item", parameters: dict):
        self._add_item_to_config(item, "marked_to_expand", parameters)

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
