from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from mir_commander.ui.utils.widget import DockWidget as BaseDockWidget

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class BaseDock(BaseDockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    def __init__(self, title: str, main_window: "MainWindow"):
        super().__init__(title, main_window)
        self.mdi_area = main_window.mdi_area
        self.docks_config = main_window.app.config.main_window.widgets.docks

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setObjectName(f"Dock.{self.__class__.__name__}")
