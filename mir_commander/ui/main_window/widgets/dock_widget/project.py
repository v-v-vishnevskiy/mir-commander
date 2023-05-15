from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QMainWindow, QTreeView

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget
from mir_commander.utils.config import Config


class Project(DockWidget):
    """The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    default_area = Qt.LeftDockWidgetArea

    def __init__(self, parent: QMainWindow, config: Config):
        super().__init__(self.tr("Project"), config, parent)
        self._tree = QTreeView(self)
        self.setWidget(self._tree)

        self._tree.setModel(QStandardItemModel(self))
        self._tree.setHeaderHidden(True)
        self._tree.setIconSize(self._icon_size())

    def set_model(self, model: QStandardItemModel):
        self._tree.setModel(model)

    def _icon_size(self) -> QSize:
        value = self.main_window.app.config.get("widgets.docks.project.icon_size", 20)
        if value > 32 or value < 16:
            value = 20
        return QSize(value, value)
