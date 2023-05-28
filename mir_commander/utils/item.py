from typing import List, Optional, Union

from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QMdiArea, QWidget

from mir_commander.data_structures.base import DataStructure
from mir_commander.ui.main_window.widgets import viewers
from mir_commander.ui.utils.widget import Action, Menu


class Item(QStandardItem):
    _viewer = None

    def __init__(self, title: str, data: Optional[DataStructure] = None):
        super().__init__(title)
        self.setData(data)
        self.setEditable(False)
        self._set_icon()
        self.file_path: str = ""

    @property
    def __mdi_area(self) -> QMdiArea:
        return self.model().parent().parent().mdi_area

    def _set_icon(self):
        self.setIcon(QIcon(f":/icons/items/{self.__class__.__name__.lower()}.png"))

    def _context_menu_actions(self) -> List[Action]:
        return []

    @property
    def path(self) -> str:
        part = str(self.row())
        parent = self.parent()
        if isinstance(parent, Item):
            return f"{parent.path}.{part}"
        else:
            return part

    def context_menu(self) -> Union[None, Menu]:
        actions = self._context_menu_actions()
        if not actions:
            return None
        menu = Menu()
        for action in actions:
            action.setParent(menu)
            menu.addAction(action)
        return menu

    def view(self, *args, **kwargs) -> Union[None, QWidget]:
        """
        Add viewer instance to MDI area and returns this viewer instance for this item
        """
        mdi_area = self.__mdi_area
        for sub_window in mdi_area.subWindowList():
            if id(sub_window.widget().item) == id(self):
                mdi_area.setActiveSubWindow(sub_window)
                return sub_window.widget()
        else:
            if self._viewer:
                viewer = self._viewer(self, *args, **kwargs)
                sub_window = self.__mdi_area.addSubWindow(viewer)
                viewer.setParent(sub_window)
                return viewer
            else:
                return None


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
