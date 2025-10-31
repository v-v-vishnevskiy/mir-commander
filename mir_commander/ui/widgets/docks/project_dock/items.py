from typing import TYPE_CHECKING, Callable

from PySide6.QtGui import QIcon, QStandardItem
from PySide6.QtWidgets import QWidget

from mir_commander.core.errors import ProjectNodeNotFoundError
from mir_commander.core.file_manager import file_manager
from mir_commander.core.project_node import ProjectNode
from mir_commander.core.project_node_registry import project_node_registry
from mir_commander.ui.utils.program import ProgramWindow
from mir_commander.ui.utils.widget import Action, Menu
from mir_commander.ui.widgets.programs.cartesian_editor.program import CartesianEditor
from mir_commander.ui.widgets.programs.molecular_visualizer.program import MolecularVisualizer

if TYPE_CHECKING:
    from .tree_view import TreeView


class TreeItem(QStandardItem):
    _id_counter = 0

    child: Callable[..., "TreeItem"]

    def __init__(self, node: ProjectNode):
        TreeItem._id_counter += 1
        self._id = TreeItem._id_counter

        super().__init__(node.name)

        self._project_node = node

        self.default_program: type[ProgramWindow] | None = None
        self.programs: list[type[ProgramWindow]] = []

        try:
            project_node = project_node_registry.get(node.type)
            icon_path = project_node.get_icon_path()
            name = project_node.get_default_program_name()
            if name == "molecular_visualizer":
                self.default_program = MolecularVisualizer
            elif name == "cartesian_editor":
                self.default_program = CartesianEditor
            names = project_node.get_program_names()
            for name in names:
                if name == "molecular_visualizer":
                    self.programs.append(MolecularVisualizer)
                elif name == "cartesian_editor":
                    self.programs.append(CartesianEditor)
        except ProjectNodeNotFoundError:
            icon_path = ":/icons/items/project-node.png"

        self.setEditable(False)
        self.setIcon(QIcon(icon_path))
        self._load_data()

    @property
    def id(self) -> int:
        return self._id

    @property
    def path(self) -> str:
        part = str(self.row())
        parent = self.parent()
        if isinstance(parent, TreeItem):
            return f"{parent.path}.{part}"
        else:
            return part

    @property
    def project_node(self) -> ProjectNode:
        return self._project_node

    def _load_data(self):
        for node in self._project_node.nodes:
            self.appendRow(TreeItem(node))

    def build_context_menu(self, tree_view: "TreeView") -> Menu | None:
        result = Menu()

        import_file_action = Action(
            text=Action.tr("Import File"), parent=result, triggered=lambda: tree_view.import_file(self)
        )
        result.addAction(import_file_action)

        for exporter in file_manager.get_exporters():
            if self.project_node.type in exporter.get_supported_node_types():
                export_item_action = Action(
                    text=Action.tr("Export..."), parent=result, triggered=lambda: tree_view.export_item(self)
                )
                result.addAction(export_item_action)
                break

        if self.default_program:

            def trigger(viewer: type[QWidget]) -> Callable[[], None]:
                return lambda: tree_view.view_item.emit(self, viewer, {})

            open_with_menu = Menu(Menu.tr("Open With"))
            for viewer in [self.default_program] + self.programs:
                action = Action(text=viewer.get_name(), parent=open_with_menu, triggered=trigger(viewer))
                open_with_menu.addAction(action)
            result.addMenu(open_with_menu)

        if self.hasChildren():
            result.addSeparator()
            view_structures_menu = Menu(Menu.tr("View Structures"), result)
            view_structures_menu.addAction(
                Action(
                    text=Action.tr("VS_Child"),
                    parent=view_structures_menu,
                    triggered=lambda: tree_view.view_item.emit(self, MolecularVisualizer, {"all": False}),
                )
            )
            view_structures_menu.addAction(
                Action(
                    text=Action.tr("VS_All"),
                    parent=view_structures_menu,
                    triggered=lambda: tree_view.view_item.emit(self, MolecularVisualizer, {"all": True}),
                )
            )
            result.addMenu(view_structures_menu)

        return result

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, name={self.text()})"
