import logging

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt
from PySide6.QtWidgets import QTreeView, QWidget

from mir_commander.core import models

from .config import ProjectDockConfig
from .items import AtomicCoordinates, AtomicCoordinatesGroup, Container, Molecule, Unex

logger = logging.getLogger(__name__)


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
        root_item = self.model().invisibleRootItem()
        for item in self._data.items:
            if type(item.data) is models.AtomicCoordinates:
                root_item.appendRow(AtomicCoordinates(item))
            elif type(item.data) is models.AtomicCoordinatesGroup:
                root_item.appendRow(AtomicCoordinatesGroup(item))
            elif type(item.data) is models.Molecule:
                root_item.appendRow(Molecule(item))
            elif type(item.data) is models.Unex:
                root_item.appendRow(Unex(item))
            else:
                root_item.appendRow(Container(item))
