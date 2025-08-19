import logging

from PySide6.QtCore import Signal, QModelIndex, QPoint, QSize, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTreeView, QWidget

from mir_commander.core import models
from mir_commander.core.parsers.consts import babushka_priehala
from mir_commander.ui.widgets.viewers.base import BaseViewer
from mir_commander.ui.widgets.viewers.molecular_structure import MolecularStructureViewer
from mir_commander.ui.utils.widget import Action, Menu

from .config import TreeConfig
from .items import AtomicCoordinates, AtomicCoordinatesGroup, Container, Item, Molecule, Unex, VolCube

logger = logging.getLogger("ProjectDock.TreeView")


class TreeView(QTreeView):
    # TODO: In fact BaseViewer should be as type[BaseViewer]. There is a bug PySide6
    view_item = Signal(QStandardItem, BaseViewer, dict)

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
        self.setModel(QStandardItemModel(parent=self))

    def _show_context_menu(self, pos: QPoint):
        item: Item = self.model().itemFromIndex(self.indexAt(pos))
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
        item = self.model().itemFromIndex(index)
        if item.default_viewer:
            self.view_item.emit(item, item.default_viewer, {})
        else:
            self.setExpanded(index, not self.isExpanded(index))

    def add_item_to_root(self, item: Item):
        root_item = self.model().invisibleRootItem()
        if type(item.data) is models.AtomicCoordinates:
            tree_item = AtomicCoordinates(item)
        elif type(item.data) is models.AtomicCoordinatesGroup:
            tree_item = AtomicCoordinatesGroup(item)
        elif type(item.data) is models.Molecule:
            tree_item = Molecule(item)
        elif type(item.data) is models.Unex:
            tree_item = Unex(item)
        elif type(item.data) is models.VolCube:
            tree_item = VolCube(item)
        else:
            tree_item = Container(item)
        root_item.appendRow(tree_item)

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
