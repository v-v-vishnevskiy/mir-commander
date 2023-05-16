from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from mir_commander.ui.utils.widget import DockWidget as BaseDockWidget
from mir_commander.utils.config import Config

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class DockWidget(BaseDockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    def __init__(self, title: str, config: Config, parent: "MainWindow"):
        super().__init__(title, parent)
        self.global_config = parent.app.config
        self.config = config

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setObjectName(f"Dock.{self.__class__.__name__}")
