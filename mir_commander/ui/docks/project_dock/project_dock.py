from typing import TYPE_CHECKING

from mir_commander.api.program import UINode
from mir_commander.core.project import Project
from mir_commander.core.project_node import ProjectNode
from mir_commander.ui.sdk.widget import DockWidget

from .config import ProjectDockConfig
from .tree_view import TreeView

if TYPE_CHECKING:
    from mir_commander.ui.project_window import ProjectWindow


class ProjectDock(DockWidget):
    """
    The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: "ProjectWindow", config: ProjectDockConfig, project: Project):
        super().__init__(self.tr("Project"), parent)
        self.project_window = parent

        self.tree = TreeView(self, project.nodes, config.tree)
        self.tree.load_data()
        self.setWidget(self.tree)

    def add_node(self, node: ProjectNode, parent: None | UINode = None):
        self.tree.add_item(node, parent)
