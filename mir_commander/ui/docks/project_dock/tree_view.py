import logging
from typing import TYPE_CHECKING, Callable, cast

from PySide6.QtCore import QModelIndex, QPoint, QSize, Qt, Signal
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTreeView

from mir_commander.api.program import UINode
from mir_commander.core.file_importers.consts import babushka_priehala
from mir_commander.core.file_manager import file_manager
from mir_commander.core.project_node import ProjectNode
from mir_commander.ui.program_manager import program_manager
from mir_commander.ui.sdk.widget import Action, Menu

from .config import TreeConfig
from .items import TreeItem

if TYPE_CHECKING:
    from .project_dock import ProjectDock

logger = logging.getLogger("UI.ProjectDock.TreeView")


class TreeView(QTreeView):
    open_item = Signal(TreeItem, str, dict)  # type: ignore[arg-type]

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
            if menu := self._build_context_menu(item):
                menu.exec(self.mapToGlobal(pos))

    def _build_context_menu(self, item: TreeItem) -> Menu | None:
        result = Menu()

        import_file_action = Action(
            text=Action.tr("Import File"), parent=result, triggered=lambda: self.import_file(item)
        )
        result.addAction(import_file_action)

        for exporter in file_manager.get_exporters():
            if item.project_node.type in exporter.get_supported_node_types():
                export_item_action = Action(
                    text=Action.tr("Export..."), parent=result, triggered=lambda: self.export_item(item)
                )
                result.addAction(export_item_action)
                break

        if item.default_program:

            def trigger(program_name: str) -> Callable[[], None]:
                return lambda: self.open_item.emit(item, program_name, {})

            open_with_menu = Menu(Menu.tr("Open With"))
            for program_name in sorted(set[str]([item.default_program] + item.programs)):
                name = program_manager.get_program(program_name).get_metadata().name
                action = Action(text=name, parent=open_with_menu, triggered=trigger(program_name))
                open_with_menu.addAction(action)
            result.addMenu(open_with_menu)

        if item.hasChildren():
            result.addSeparator()
            view_structures_menu = Menu(Menu.tr("View Structures"), result)
            view_structures_menu.addAction(
                Action(
                    text=Action.tr("VS_Child"),
                    parent=view_structures_menu,
                    triggered=lambda: self.open_item.emit(item, "molecular_visualizer", {"all": False}),
                )
            )
            view_structures_menu.addAction(
                Action(
                    text=Action.tr("VS_All"),
                    parent=view_structures_menu,
                    triggered=lambda: self.open_item.emit(item, "molecular_visualizer", {"all": True}),
                )
            )
            result.addMenu(view_structures_menu)

        return result

    def _item_double_clicked(self, index: QModelIndex):
        item: TreeItem = cast(TreeItem, self._model.itemFromIndex(index))
        if item.default_program:
            self.open_item.emit(item, item.default_program, {})
        else:
            self.setExpanded(index, not self.isExpanded(index))

    def import_file(self, parent: TreeItem):
        self._project_window.import_file(parent)

    def export_item(self, item: TreeItem):
        self._project_window.export_file(item.project_node)

    def add_item(self, node: ProjectNode, parent: UINode | None = None):
        parent_item = parent if parent is not None else self._model.invisibleRootItem()
        parent_item.appendRow(TreeItem(node))

    def load_data(self):
        logger.debug("Loading data ...")
        self._model.clear()
        for node in self._nodes:
            self.add_item(node)

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
                self.open_item.emit(item, item.default_program, {})
        for i in range(item.rowCount()):
            self._view_babushka(item.child(i))
