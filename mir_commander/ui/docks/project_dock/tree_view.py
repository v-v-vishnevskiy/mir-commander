import logging
from typing import TYPE_CHECKING, Callable, cast

from PySide6.QtCore import QCoreApplication, QModelIndex, QPoint, QSize, Qt, Signal
from PySide6.QtGui import QAction, QStandardItemModel
from PySide6.QtWidgets import QMenu, QTreeView

from mir_commander.api.program import UINode
from mir_commander.api.project_node_schema import ActionType
from mir_commander.core.plugins_registry import plugins_registry
from mir_commander.core.errors import PluginDisabledError, PluginNotFoundError, ProjectNodeNotFoundError
from mir_commander.core.file_manager import FileManager
from mir_commander.core.project_node import ProjectNode
from mir_commander.ui.config import ImportFileRulesConfig

from .config import TreeConfig
from .items import TreeItem

if TYPE_CHECKING:
    from .project_dock import ProjectDock

logger = logging.getLogger("UI.ProjectDock")


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
        self._file_manager = FileManager(plugins_registry)

    def _show_context_menu(self, pos: QPoint):
        item: TreeItem = cast(TreeItem, self._model.itemFromIndex(self.indexAt(pos)))
        if item:
            if menu := self._build_context_menu(item):
                menu.exec(self.mapToGlobal(pos))

    def _build_context_menu(self, item: TreeItem) -> QMenu | None:
        result = QMenu()

        import_file_action = QAction(text=self.tr("Import File"), parent=result)
        import_file_action.triggered.connect(lambda: self.import_file(item))
        result.addAction(import_file_action)

        for exporter in self._file_manager.get_exporters():
            if item.project_node.type in exporter.plugin.details.supported_node_types:
                export_item_action = QAction(text=self.tr("Export..."), parent=result)
                export_item_action.triggered.connect(lambda: self.export_item(item))
                result.addAction(export_item_action)
                break

        if item.default_program:

            def trigger(program_id: str) -> Callable[[], None]:
                return lambda: self.open_item.emit(item, program_id, {})

            programs = []
            for program_id in sorted(set[str]([item.default_program] + item.programs)):
                try:
                    programs.append((program_id, plugins_registry.program.get(program_id).metadata.name))
                except (PluginNotFoundError, PluginDisabledError):
                    continue

            if programs:
                open_with_menu = QMenu(self.tr("Open With"))
                for program_id, program_name in programs:
                    action = QAction(text=QCoreApplication.translate(program_id, program_name), parent=open_with_menu)
                    action.triggered.connect(trigger(program_id))
                    open_with_menu.addAction(action)
                result.addMenu(open_with_menu)

        if item.hasChildren():
            result.addSeparator()
            view_structures_menu = QMenu(self.tr("View Structures"), result)
            action_vs_child = QAction(text=self.tr("VS_Child"), parent=view_structures_menu)
            action_vs_child.triggered.connect(
                lambda: self.open_item.emit(item, "builtin.molecular_visualizer", {"all": False})
            )
            view_structures_menu.addAction(action_vs_child)
            action_vs_all = QAction(text=self.tr("VS_All"), parent=view_structures_menu)
            action_vs_all.triggered.connect(
                lambda: self.open_item.emit(item, "builtin.molecular_visualizer", {"all": True})
            )
            view_structures_menu.addAction(action_vs_all)
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
        try:
            parent_item.appendRow(TreeItem(node))
        except ProjectNodeNotFoundError:
            logger.error("Project node type not found: %s", node.type)

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

    def open_auto_open_nodes(self, import_config: ImportFileRulesConfig, is_startup: bool):
        """Open nodes marked for auto-opening after import."""
        root_item = self._model.invisibleRootItem()
        for i in range(root_item.rowCount()):
            self._open_auto_open_nodes(cast(TreeItem, root_item.child(i)), import_config, is_startup)

    def _open_auto_open_nodes(self, item: TreeItem, import_config: ImportFileRulesConfig, is_startup: bool):
        """Recursively open nodes marked with auto_open flag."""
        node = item.project_node
        if node is not None and ActionType.OPEN in node.actions:
            node.actions.remove(ActionType.OPEN)

            should_open = (
                import_config.get_open_on_startup(node.type)
                if is_startup
                else import_config.get_open_on_import(node.type)
            )

            if should_open:
                programs = import_config.get_programs(node.type)
                if len(programs) < 1:
                    if item.default_program:
                        self.open_item.emit(item, item.default_program, {})
                else:
                    for program in programs:
                        if program in item.programs:
                            self.open_item.emit(item, program, {})

        for i in range(item.rowCount()):
            self._open_auto_open_nodes(cast(TreeItem, item.child(i)), import_config, is_startup)
