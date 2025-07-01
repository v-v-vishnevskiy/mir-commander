import logging

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTreeView, QWidget

from mir_commander.core import models
from mir_commander.core.parsers.consts import babushka_priehala

from .config import ProjectDockConfig
from .items import AtomicCoordinates, AtomicCoordinatesGroup, Container, Molecule, Unex

logger = logging.getLogger("ProjectDock.TreeView")


class TreeView(QTreeView):
    def __init__(self, parent: QWidget, data: models.Data, config: ProjectDockConfig):
        super().__init__(parent)

        self._data = data

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        icon_size = config.tree.icon_size
        self.setIconSize(QSize(icon_size, icon_size))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showContextMenu)
        self.doubleClicked.connect(self._item_double_clicked)
        self.setModel(QStandardItemModel(parent=self))

    def _showContextMenu(self, pos: QPoint):
        item = self.model().itemFromIndex(self.indexAt(pos))
        if item:
            menu = item.context_menu()
            if not menu.isEmpty():
                menu.exec(self.mapToGlobal(pos))

    def _item_double_clicked(self, index: QModelIndex):
        item = self.model().itemFromIndex(index)
        if viewer := item.view():
            viewer.showNormal()
        else:
            self.setExpanded(index, not self.isExpanded(index))

    def load_data(self):
        logger.debug("Loading data ...")
        root_item = self.model().invisibleRootItem()
        for item in self._data.items:
            if type(item.data) is models.AtomicCoordinates:
                tree_item = AtomicCoordinates(item)
            elif type(item.data) is models.AtomicCoordinatesGroup:
                tree_item = AtomicCoordinatesGroup(item)
            elif type(item.data) is models.Molecule:
                tree_item = Molecule(item)
            elif type(item.data) is models.Unex:
                tree_item = Unex(item)
            else:
                tree_item = Container(item)
            root_item.appendRow(tree_item)

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
            item.view()
        for i in range(item.rowCount()):
            self._view_babushka(item.child(i))
