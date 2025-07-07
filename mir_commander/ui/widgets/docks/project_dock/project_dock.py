from PySide6.QtWidgets import QWidget

from mir_commander.core import Project
from mir_commander.core.models.item import Item

from ..base import BaseDock
from .config import ProjectDockConfig
from .tree_view import TreeView


class ProjectDock(BaseDock):
    """
    The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: QWidget, config: ProjectDockConfig, project: Project):
        super().__init__(self.tr("Project"), parent)
        self._project = project
        self.tree = TreeView(self, project.data, config.tree)
        self.tree.load_data()
        self.setWidget(self.tree)

    def add_item_to_root(self, item: Item):
        self.tree.add_item_to_root(item)
