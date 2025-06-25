from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTreeView

from mir_commander.parsers.utils import ItemParametrized

from .base import BaseDock
from .config import DocksConfig

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class TreeView(QTreeView):
    def __init__(self, parent: BaseDock, config: DocksConfig):
        super().__init__(parent)

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        icon_size = config.project.tree.icon_size
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


class ProjectDock(BaseDock):
    """The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: "MainWindow"):
        super().__init__(self.tr("Project"), parent)
        self._tree = TreeView(self, self.docks_config)
        self.setWidget(self._tree)

    def set_model(self, model: QStandardItemModel):
        model.setParent(self._tree)
        self._tree.setModel(model)

    def expand_items(self, config_items: list[ItemParametrized]):
        for config_item in config_items:
            item = config_item.item
            self._tree.setExpanded(self._tree.model().indexFromItem(item), True)
