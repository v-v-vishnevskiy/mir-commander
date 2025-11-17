from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QDockWidget


class BaseDock(QDockWidget):
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

        self.setObjectName(f"Dock.{self._get_name()}")

        self.setContentsMargins(0, 0, 0, 0)

    def _get_name(self) -> str:
        return self.__class__.__name__
