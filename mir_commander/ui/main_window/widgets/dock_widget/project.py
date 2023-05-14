from PySide6.QtCore import QSize
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTreeView, QWidget

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget


class Project(DockWidget):
    """The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: QWidget):
        super().__init__(self.tr("Project"), parent)
        self._tree = QTreeView(self)
        self.setWidget(self._tree)

        self._tree.setModel(QStandardItemModel(self))
        self._tree.setHeaderHidden(True)
        self._tree.setIconSize(QSize(20, 20))

    def set_model(self, model: QStandardItemModel):
        self._tree.setModel(model)
