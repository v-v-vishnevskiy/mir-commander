from typing import TYPE_CHECKING, Type

from PySide6.QtGui import QIcon, QStandardItem, Qt
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from mir_commander.core import models
from mir_commander.ui.widgets.viewers.molecular_structure.viewer import MolecularStructure
from mir_commander.ui.utils.widget import Action, Menu

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class Item(QStandardItem):
    default_viewer: Type[QWidget] | None = None

    def __init__(self, data: models.Item):
        super().__init__(data.name)
        self.setData(data)
        self.setEditable(False)
        self._set_icon()
        self.load_data()

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
        self._create_viewer_and_add_to_mdi(MolecularStructure, all=True).show()

    def _view_structures_child(self):
        self._create_viewer_and_add_to_mdi(MolecularStructure, all=False).show()

    def _create_viewer_and_add_to_mdi(self, cls: Type[QWidget], maximize: bool = False, *args, **kwargs) -> QWidget:
        """
        Create viewer instance and add it to MDI area and return this viewer instance
        """
        sub_window = QMdiSubWindow(parent=self._mdi_area)
        sub_window.setAttribute(Qt.WA_DeleteOnClose)
        viewer = cls(
            parent=sub_window,
            config=self._main_window.config.widgets.viewers,
            item=self,
            *args, 
            **kwargs,
        )
        viewer.short_msg.connect(self._main_window.status_bar.showMessage)
        viewer.long_msg.connect(self._main_window.docks.console.append)
        sub_window.setWidget(viewer)
        self._mdi_area.addSubWindow(sub_window)
        if maximize:
            sub_window.showMaximized()
        return viewer

    def view(self, maximize: bool = False, *args, **kwargs) -> None | QWidget:
        """
        Check for existing viewer and create if doesn't exist
        """
        mdi_area = self._mdi_area
        for sub_window in mdi_area.subWindowList():
            # checking if viewer for this item already opened
            if id(sub_window.widget().item) == id(self):
                mdi_area.setActiveSubWindow(sub_window)
                return sub_window.widget()
        else:
            if self.default_viewer:
                return self._create_viewer_and_add_to_mdi(self.default_viewer, maximize, *args, **kwargs)
            else:
                return None

    def load_data(self):
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


class AtomicCoordinatesGroup(Item):
    default_viewer = MolecularStructure

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates-folder.png"))


class AtomicCoordinates(Item):
    default_viewer = MolecularStructure

    def context_menu(self) -> Menu:
        return Menu()

    def _set_icon(self):
        self.setIcon(QIcon(":/icons/items/coordinates.png"))
