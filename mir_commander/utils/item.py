from typing import Optional, Union

from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QWidget

from mir_commander.data_structures.base import DataStructure
from mir_commander.ui.main_window.widgets import viewers


class Item(QStandardItem):
    _viewer = None

    def __init__(self, title: str, data: Optional[DataStructure] = None):
        super().__init__(title)
        self.setData(data)
        self.setEditable(False)
        self._set_icon()
        self.file_path: str = ""

    def _set_icon(self):
        self.setIcon(QIcon(f":/icons/items/{self.__class__.__name__.lower()}.png"))

    def viewer(self) -> Union[None, QWidget]:
        """
        Returns appropriate viewer instance for this item
        """
        return self._viewer(self) if self._viewer else None  # type: ignore

    @property
    def path(self) -> str:
        part = str(self.row())
        parent = self.parent()
        if isinstance(parent, Item):
            return f"{parent.path}.{part}"
        else:
            return part


class Group(Item):
    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/folder.png"))


class Molecule(Item):
    _viewer = viewers.Molecule  # type: ignore


class AtomicCoordinatesGroup(Group):
    def __init__(self, title: str = "Atomic Coordinates", data: Optional[DataStructure] = None):
        super().__init__(title, data)

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates-folder.png"))


class AtomicCoordinates(Item):
    _viewer = viewers.AtomicCoordinates  # type: ignore

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates.png"))
