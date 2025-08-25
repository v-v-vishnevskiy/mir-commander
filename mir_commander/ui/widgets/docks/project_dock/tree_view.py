import logging
from typing import cast

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTreeView, QWidget

from mir_commander.core import models
from mir_commander.core.parsers.consts import babushka_priehala
from mir_commander.ui.utils.viewer import Viewer
from mir_commander.ui.utils.widget import Action, Menu
from mir_commander.ui.widgets.viewers.molecular_structure.viewer import MolecularStructureViewer

from .config import TreeConfig
from .items import AtomicCoordinates, AtomicCoordinatesGroup, Container, Item, Molecule, Unex, VolCube

logger = logging.getLogger("ProjectDock.TreeView")


class TreeView(QTreeView):
    view_item = Signal(QStandardItem, Viewer.__class__, dict)  # type: ignore[arg-type]

    def __init__(self, parent: QWidget, data: models.Data, config: TreeConfig):
        super().__init__(parent)

        self._data = data

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        icon_size = config.icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.doubleClicked.connect(self._item_double_clicked)
        self._model = QStandardItemModel(parent=self)
        self.setModel(self._model)

    def _show_context_menu(self, pos: QPoint):
        item: Item = cast(Item, self._model.itemFromIndex(self.indexAt(pos)))
        if item and item.context_menu:
            menu = self._build_context_menu(item)
            menu.exec(self.mapToGlobal(pos))

    def _build_context_menu(self, item: Item) -> Menu:
        result = Menu()

        view_structures_menu = Menu(Menu.tr("View Structures"), result)
        view_structures_menu.addAction(
            Action(
                text=Action.tr("VS_Child"),
                parent=view_structures_menu,
                triggered=lambda: self.view_item.emit(item, MolecularStructureViewer, {"all": False}),
            )
        )
        view_structures_menu.addAction(
            Action(
                text=Action.tr("VS_All"),
                parent=view_structures_menu,
                triggered=lambda: self.view_item.emit(item, MolecularStructureViewer, {"all": True}),
            )
        )
        view_structures_menu.addSeparator()

        result.addMenu(view_structures_menu)
        return result

    def _item_double_clicked(self, index: QModelIndex):
        item: Item = cast(Item, self._model.itemFromIndex(index))
        if item.default_viewer:
            self.view_item.emit(item, item.default_viewer, {})
        else:
            self.setExpanded(index, not self.isExpanded(index))

    def add_item_to_root(self, item: models.Item):
        root_item = self._model.invisibleRootItem()
        if type(item.data) is models.AtomicCoordinates:
            root_item.appendRow(AtomicCoordinates(item))
        elif type(item.data) is models.AtomicCoordinatesGroup:
            root_item.appendRow(AtomicCoordinatesGroup(item))
        elif type(item.data) is models.Molecule:
            root_item.appendRow(Molecule(item))
        elif type(item.data) is models.Unex:
            root_item.appendRow(Unex(item))
        elif type(item.data) is models.VolCube:
            root_item.appendRow(VolCube(item))
        else:
            root_item.appendRow(Container(item))

    def load_data(self):
        logger.debug("Loading data ...")
        for item in self._data.items:
            self.add_item_to_root(item)

    def expand_top_items(self):
        logger.debug("Expanding top items ...")
        root_item = self.model().invisibleRootItem()
        for i in range(root_item.rowCount()):
            self.setExpanded(self.model().indexFromItem(root_item.child(i)), True)

    def view_babushka(self):
        logger.debug("Opening items in respective viewers ...")
        self._view_babushka(self.model().invisibleRootItem())

    def _view_babushka(self, item):
        data = item.data()
        if data is not None and data.metadata.get(babushka_priehala, False):
            if item.default_viewer:
                self.view_item.emit(item, item.default_viewer, {})
        for i in range(item.rowCount()):
            self._view_babushka(item.child(i))
