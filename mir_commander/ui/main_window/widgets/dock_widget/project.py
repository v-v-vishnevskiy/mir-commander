from PySide6.QtCore import QT_TRANSLATE_NOOP
from PySide6.QtWidgets import QWidget

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget


class Project(DockWidget):
    """The project dock widget.

    A single instance of this class is created
    for showing a tree widget with objects of the project.
    """

    def __init__(self, parent: QWidget):
        super().__init__(QT_TRANSLATE_NOOP("DockNames", "Project"), parent)
        # ToDo: self.setWidget(self.project_tree)
