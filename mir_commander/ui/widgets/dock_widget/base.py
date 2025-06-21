from typing import TYPE_CHECKING

from PySide6.QtCore import Qt

from mir_commander.ui.utils.widget import DockWidget as BaseDockWidget

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class DockWidget(BaseDockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    config_key: str = ""

    def __init__(self, title: str, parent: "MainWindow"):
        super().__init__(title, parent)
        self.mdi_area = parent.mdi_area
        self.global_config = parent.app.config
        self.config = self.global_config.nested(self.config_key)

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self.setObjectName(f"Dock.{self.__class__.__name__}")
