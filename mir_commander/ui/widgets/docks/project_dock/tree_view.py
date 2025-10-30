import logging
from typing import TYPE_CHECKING, cast

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTreeView

from mir_commander.core.file_importers.consts import babushka_priehala
from mir_commander.core.project_node import ProjectNode
from mir_commander.ui.utils.program import ProgramWindow

from .config import TreeConfig
from .items import TreeItem

if TYPE_CHECKING:
    from .project_dock import ProjectDock

logger = logging.getLogger("UI.ProjectDock.TreeView")


class TreeView(QTreeView):
    view_item = Signal(QStandardItem, ProgramWindow.__class__, dict)  # type: ignore[arg-type]

    def __init__(self, parent: "ProjectDock", nodes: list[ProjectNode], config: TreeConfig):
        super().__init__(parent)

        self._project_window = parent.project_window
        self._nodes = nodes
        self._model = QStandardItemModel()

        icon_size = config.icon_size

        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.doubleClicked.connect(self._item_double_clicked)
        self.setModel(self._model)

    def _show_context_menu(self, pos: QPoint):
        item: TreeItem = cast(TreeItem, self._model.itemFromIndex(self.indexAt(pos)))
        if item:
            if menu := item.build_context_menu(self):
                menu.exec(self.mapToGlobal(pos))

    def _item_double_clicked(self, index: QModelIndex):
        item: TreeItem = cast(TreeItem, self._model.itemFromIndex(index))
        if item.default_program:
            self.view_item.emit(item, item.default_program, {})
        else:
            self.setExpanded(index, not self.isExpanded(index))

    def import_file(self, item: TreeItem):
        self._project_window.import_file(item)

    def export_item(self, item: TreeItem):
        self._project_window.export_file(item.project_node)

    def _add_item(self, node: ProjectNode, parent: TreeItem | None = None):
        parent_item = parent if parent is not None else self._model.invisibleRootItem()
        parent_item.appendRow(TreeItem(node))

    def load_data(self):
        logger.debug("Loading data ...")
        self._model.clear()
        for node in self._nodes:
            self._add_item(node)

    def expand_top_items(self):
        logger.debug("Expanding top items ...")
        root_item = self._model.invisibleRootItem()
        for i in range(root_item.rowCount()):
            self.setExpanded(self._model.indexFromItem(root_item.child(i)), True)

    def view_babushka(self):
        logger.debug("Opening items in respective programs ...")
        root_item = self._model.invisibleRootItem()
        for i in range(root_item.rowCount()):
            self._view_babushka(cast(TreeItem, root_item.child(i)))

    def _view_babushka(self, item: TreeItem):
        data = item.project_node
        if data is not None and data.metadata.pop(babushka_priehala, False):
            if item.default_program:
                self.view_item.emit(item, item.default_program, {})
        for i in range(item.rowCount()):
            self._view_babushka(item.child(i))
