from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTreeView

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget
from mir_commander.utils.config import Config

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class TreeView(QTreeView):
    def __init__(self, parent: DockWidget, config: Config):
        super().__init__(parent)
        self._config = config

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self.setIconSize(self._icon_size())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._showContextMenu)
        self.doubleClicked.connect(self._item_double_clicked)

    def _icon_size(self) -> QSize:
        value = self._config["icon_size"]
        if value > 32 or value < 16:
            value = 20
        return QSize(value, value)

    def _showContextMenu(self, pos: QPoint):
        item = self.model().itemFromIndex(self.indexAt(pos))
        if item:
            menu = item.context_menu()
            if not menu.isEmpty():
                menu.exec(self.mapToGlobal(pos))

    def _item_double_clicked(self, index: QModelIndex):
        item = self.model().itemFromIndex(index)
        if viewer := item.view():
            viewer.show()
        else:
            self.setExpanded(index, not self.isExpanded(index))


class Project(DockWidget):
    """The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    config_key: str = "widgets.docks.project"

    def __init__(self, parent: "MainWindow"):
        super().__init__(self.tr("Project"), parent)
        self._tree = TreeView(self, self.config.nested("tree"))
        self.setWidget(self._tree)

    def set_model(self, model: QStandardItemModel):
        model.setParent(self._tree)
        self._tree.setModel(model)
