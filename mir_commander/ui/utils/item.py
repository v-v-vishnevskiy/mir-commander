from typing import TYPE_CHECKING, Type

from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from mir_commander.data_structures.base import DataStructure
from mir_commander.ui.main_window.widgets import viewers
from mir_commander.ui.utils.widget import Action, Menu

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class Item(QStandardItem):
    default_viewer: Type[QWidget] | None = None

    def __init__(self, title: str, data: None | DataStructure = None):
        super().__init__(title)
        self.setData(data)
        self.setEditable(False)
        self._set_icon()
        self.file_path: str = ""

    @property
    def _mdi_area(self) -> QMdiArea:
        return self.model().parent().parent().mdi_area

    @property
    def _main_window(self) -> "MainWindow":
        return self.model().parent().parent().parent()

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

    def context_menu(self) -> Menu:
        result = Menu()

        view_structures_menu = Menu(Menu.tr("View Structures"), result)
        view_structures_menu.addAction(
            Action(Action.tr("VS_Child"), view_structures_menu, triggered=self._view_structures_child)
        )
        view_structures_menu.addAction(
            Action(Action.tr("VS_All"), view_structures_menu, triggered=self._view_structures_all)
        )
        view_structures_menu.addSeparator()

        result.addMenu(view_structures_menu)
        return result

    def _view_structures_all(self):
        self._viewer(viewers.MolecularStructure, all=True).show()

    def _view_structures_child(self):
        self._viewer(viewers.MolecularStructure, all=False).show()

    def _viewer(self, cls: Type[QWidget], maximize: bool = False, *args, **kwargs) -> QWidget:
        sub_window = QMdiSubWindow(self._mdi_area)
        viewer = cls(sub_window, item=self, main_window=self._main_window, *args, **kwargs)
        sub_window.setWidget(viewer)
        self._mdi_area.addSubWindow(sub_window)
        if maximize:
            sub_window.showMaximized()
        return viewer

    def view(self, maximize: bool = False, *args, **kwargs) -> None | QWidget:
        """
        Add viewer instance to MDI area and returns this viewer instance for this item
        """
        mdi_area = self._mdi_area
        for sub_window in mdi_area.subWindowList():
            # checking if viewer for this item already opened
            if id(sub_window.widget().item) == id(self):
                mdi_area.setActiveSubWindow(sub_window)
                return sub_window.widget()
        else:
            if self.default_viewer:
                return self._viewer(self.default_viewer, maximize, *args, **kwargs)
            else:
                return None


class Group(Item):
    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/folder.png"))


class Molecule(Item):
    pass


class UnexProject(Item):
    pass


class AtomicCoordinatesGroup(Group):
    default_viewer = viewers.MolecularStructure

    def __init__(self, title: str = "Atomic Coordinates", data: DataStructure | None = None):
        super().__init__(title, data)

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates-folder.png"))


class AtomicCoordinates(Item):
    default_viewer = viewers.MolecularStructure

    def context_menu(self) -> Menu:
        return Menu()

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates.png"))
