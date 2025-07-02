from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMdiArea, QWidget

from mir_commander.ui.utils.widget import DockWidget as BaseDockWidget


class BaseDock(BaseDockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    def __init__(self, title: str, parent: QWidget, mdi_area: QMdiArea):
        super().__init__(title, parent)
        self.mdi_area = mdi_area

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setObjectName(f"Dock.{self.__class__.__name__}")
