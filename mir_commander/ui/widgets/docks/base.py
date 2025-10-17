from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from mir_commander.ui.utils.widget import DockWidget


class BaseDock(DockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    def __init__(self, title: str, parent: QWidget):
        super().__init__(title, parent)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setObjectName(f"Dock.{self.__class__.__name__}")

        self.setContentsMargins(0, 0, 0, 0)
