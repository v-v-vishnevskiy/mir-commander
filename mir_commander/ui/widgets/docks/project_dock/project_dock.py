from PySide6.QtWidgets import QMdiArea, QWidget

from mir_commander.core import Project

from ..base import BaseDock
from .config import ProjectDockConfig
from .tree_view import TreeView


class ProjectDock(BaseDock):
    """
    The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: QWidget, mdi_area: QMdiArea, config: ProjectDockConfig, project: Project):
        super().__init__(self.tr("Project"), parent, mdi_area)
        self._project = project
        self._tree = TreeView(self, project.data, config)
        self._tree.load_data()

        if project.is_temporary:
            self._tree.expand_top_items()
            self._tree.view_babushka()

        self.setWidget(self._tree)
