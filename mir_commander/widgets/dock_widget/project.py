from PySide6.QtWidgets import QWidget

from mir_commander.widgets.dock_widget.base import DockWidget


class Project(DockWidget):
    def __init__(self, parent: QWidget):
        super().__init__("Project", parent)
        # ToDo: self.setWidget(self.project_tree)
