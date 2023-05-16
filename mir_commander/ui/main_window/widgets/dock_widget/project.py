from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTreeView

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget
from mir_commander.utils.config import Config

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class Project(DockWidget):
    """The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: "MainWindow", config: Config):
        super().__init__(self.tr("Project"), config, parent)
        self._tree = QTreeView(self)
        self.setWidget(self._tree)

        self._tree.setModel(QStandardItemModel(self))
        self._tree.setHeaderHidden(True)
        self._tree.setIconSize(self._icon_size())

    def set_model(self, model: QStandardItemModel):
        self._tree.setModel(model)

    def _icon_size(self) -> QSize:
        value = self.global_config.get("widgets.docks.project.icon_size", 20)
        if value > 32 or value < 16:
            value = 20
        return QSize(value, value)
