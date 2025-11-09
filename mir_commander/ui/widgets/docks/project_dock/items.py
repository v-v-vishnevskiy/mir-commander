from typing import Callable, Self

from PySide6.QtGui import QIcon

from mir_commander.api.program import UINode
from mir_commander.core.errors import ProjectNodeNotFoundError
from mir_commander.core.project_node import ProjectNode
from mir_commander.core.project_node_registry import project_node_registry
from mir_commander.ui.program_manager import program_manager


class TreeItem(UINode):
    _id_counter = 0

    child: Callable[..., Self]

    def __init__(self, node: ProjectNode):
        super().__init__(node.name)
        self.setEditable(False)

        TreeItem._id_counter += 1
        self._id = TreeItem._id_counter

        self._project_node = node

        self.default_program: str | None = None
        self.programs: list[str] = []
        for program in program_manager.programs:
            if node.type in program.get_supported_node_types():
                self.programs.append(program.get_name())
            if node.type in program.is_default_for_node_type():
                self.default_program = program.get_name()

        try:
            icon_path = project_node_registry.get(node.type).get_icon_path()
        except ProjectNodeNotFoundError:
            icon_path = ":/icons/items/project-node.png"
        self.setIcon(QIcon(icon_path))

        self._load_data()

    @property
    def id(self) -> int:
        return self._id

    @property
    def project_node(self) -> ProjectNode:
        return self._project_node

    def _load_data(self):
        for node in self._project_node.nodes:
            self.appendRow(TreeItem(node))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, name={self.text()})"
