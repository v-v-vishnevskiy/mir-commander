from typing import TYPE_CHECKING

from mir_commander.core import Project

from ..base import BaseDock
from .config import ProjectDockConfig
from .tree_view import TreeView

if TYPE_CHECKING:
    from mir_commander.ui.project_window import ProjectWindow


class ProjectDock(BaseDock):
    """
    The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: "ProjectWindow", config: ProjectDockConfig, project: Project):
        super().__init__(self.tr("Project"), parent)
        self.project_window = parent

        self.tree = TreeView(self, project.data, config.tree)
        self.tree.load_data()
        self.setMinimumWidth(200)
        self.setWidget(self.tree)
