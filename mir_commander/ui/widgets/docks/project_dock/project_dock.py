from typing import TYPE_CHECKING

from PySide6.QtGui import QStandardItemModel

from mir_commander.core import Project
# from mir_commander.parsers.utils import ItemParametrized

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

        self._model = QStandardItemModel(parent=self._tree)
        self._tree.setModel(self._model)
        self._tree.load_data()

        self.setWidget(self._tree)

    # def expand_items(self, config_items: list[ItemParametrized]):
    #     for config_item in config_items:
    #         item = config_item.item
    #         self._tree.setExpanded(self._tree.model().indexFromItem(item), True)
