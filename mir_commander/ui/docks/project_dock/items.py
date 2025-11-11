from typing import Callable, Self

from PySide6.QtGui import QIcon

from mir_commander.api.program import UINode
from mir_commander.core import plugins_registry
from mir_commander.core.errors import ProjectNodeNotFoundError
from mir_commander.core.project_node import ProjectNode


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
        for item in plugins_registry.program.get_all():
            if item.enabled is False:
                continue
            program = item.plugin
            if node.type in program.details.supported_node_types:
                self.programs.append(item.id)
            if node.type in program.details.is_default_for_node_type:
                self.default_program = item.id

        try:
            icon_path = plugins_registry.project_node.get(node.type).details.icon_path
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
