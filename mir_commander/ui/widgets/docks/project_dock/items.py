from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QWidget

from mir_commander.core import models
from mir_commander.ui.widgets.viewers.molecular_structure import MolecularStructureViewer


class Item(QStandardItem):
    default_viewer: type[QWidget] | None = None
    context_menu: bool = True

    def __init__(self, data: models.Item):
        super().__init__(data.name)
        self.setData(data)
        self.setEditable(False)
        self._set_icon()
        self._load_data()

    def _set_icon(self):
        self.setIcon(QIcon(f":/icons/items/{self.__class__.__name__.lower()}.png"))

    @property
    def path(self) -> str:
        part = str(self.row())
        parent = self.parent()
        if isinstance(parent, Item):
            return f"{parent.path}.{part}"
        else:
            return part

    def _load_data(self):
        data: models.Item = self.data()

        for item in data.items:
            if type(item.data) is models.AtomicCoordinates:
                self.appendRow(AtomicCoordinates(item))
            elif type(item.data) is models.AtomicCoordinatesGroup:
                self.appendRow(AtomicCoordinatesGroup(item))
            elif type(item.data) is models.Molecule:
                self.appendRow(Molecule(item))
            elif type(item.data) is models.Unex:
                self.appendRow(Unex(item))
            else:
                self.appendRow(Container(item))


class Container(Item):
    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/folder.png"))


class Molecule(Item):
    pass


class Unex(Item):
    pass


class VolCube(Item):
    pass

class AtomicCoordinatesGroup(Item):
    default_viewer = MolecularStructureViewer

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates-folder.png"))


class AtomicCoordinates(Item):
    default_viewer = MolecularStructureViewer
    context_menu: bool = False

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates.png"))
