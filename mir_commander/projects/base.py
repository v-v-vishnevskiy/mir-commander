from pathlib import Path

from PySide6.QtGui import QStandardItem, QStandardItemModel

from mir_commander.parsers import ItemParametrized

from .config import Config


class Project:
    """The most basic class of projects."""

    def __init__(self, path: Path, config: Config):
        self.path = path
        self.config = config
        self.model = QStandardItemModel()

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def root_item(self) -> QStandardItem:
        return self.model.invisibleRootItem()

    @property
    def is_temporary(self) -> bool:
        return False

    def _get_items_from_config(self, category: str) -> list[ItemParametrized]:
        result = []
        for item_dict in self.config.items.get(category, []):
            if item := self._item(item_dict["path"].split("."), self.root_item):
                result.append(ItemParametrized(item, item_dict["parameters"]))
        return result

    @property
    def items_marked_to_view(self) -> list[ItemParametrized]:
        """
        Returns list of items marked as (to be) opened in viewer(s)
        """
        return self._get_items_from_config("marked_to_view")

    @property
    def items_marked_to_expand(self) -> list[ItemParametrized]:
        """
        Returns list of items marked as expanded
        """
        return self._get_items_from_config("marked_to_expand")

    def _add_item_to_config(self, itempar: ItemParametrized, category: str):
        entries = self.config.items.get(category, [])
        path = itempar.item.path
        if path not in entries:
            entries.append({"path": path, "parameters": itempar.parameters})
        self.config.items[category] = entries

    def mark_item_to_view(self, itempar: ItemParametrized):
        self._add_item_to_config(itempar, "marked_to_view")

    def mark_item_to_expand(self, itempar: ItemParametrized):
        self._add_item_to_config(itempar, "marked_to_expand")

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
