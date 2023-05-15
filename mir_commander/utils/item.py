from typing import Optional

from PySide6.QtGui import QIcon, QStandardItem

from mir_commander.data_structures.base import DataStructure


class Item(QStandardItem):
    def __init__(self, title: str, data: Optional[DataStructure] = None):
        super().__init__(title)
        self.setData(data)
        self.setEditable(False)
        self._set_icon()
        self.file_path: str = ""

    def _set_icon(self):
        self.setIcon(QIcon(f":/icons/items/{self.__class__.__name__.lower()}.png"))


class Group(Item):
    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/folder.png"))


class Molecule(Item):
    pass


class AtomicCoordinatesGroup(Group):
    def __init__(self, title: str = "Atomic Coordinates", data: Optional[DataStructure] = None):
        super().__init__(title, data)

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates-folder.png"))


class AtomicCoordinates(Item):
    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates.png"))
