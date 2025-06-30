from typing import TYPE_CHECKING

from mir_commander.core import Project

from ..base import BaseDock
from .tree_view import TreeView

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class ProjectDock(BaseDock):
    """
    The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: "MainWindow", project: Project):
        super().__init__(self.tr("Project"), parent)
        self._project = project
        self._tree = TreeView(self, project.data, self.docks_config.project)
        self._tree.load_data(project.is_temporary)

        if project.is_temporary:
            self._tree.view_babushka()

        self.setWidget(self._tree)
