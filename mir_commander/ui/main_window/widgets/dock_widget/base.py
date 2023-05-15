from PySide6.QtCore import Qt
from PySide6.QtGui import QMoveEvent, QResizeEvent
from PySide6.QtWidgets import QMainWindow

from mir_commander.ui.utils.widget import DockWidget as BaseDockWidget
from mir_commander.utils.config import Config


class DockWidget(BaseDockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    default_area: Qt.DockWidgetArea = None

    def __init__(self, title: str, config: Config, parent: QMainWindow):
        super().__init__(title, parent)
        self.main_window = parent
        self.config = config

        self.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )

        self._restore_settings()

        self.dockLocationChanged.connect(self._location_changed)
        self.visibilityChanged.connect(self._visibility_changed)

    def moveEvent(self, event: QMoveEvent):
        self.config["pos"] = [event.pos().x(), event.pos().y()]

    def resizeEvent(self, event: QResizeEvent):
        self.config["size"] = [event.size().width(), event.size().height()]

    def _location_changed(self, area: Qt.DockWidgetArea):
        self.config["area"] = area.name

    def _visibility_changed(self, visible: bool):
        self.config["visible"] = visible

    def _restore_area(self):
        """
        :return: True if the area was restored; otherwise returns False.
        """
        if area := self.config["area"]:
            try:
                area = getattr(Qt.DockWidgetArea, area)
                if area == Qt.DockWidgetArea.NoDockWidgetArea:
                    self.main_window.addDockWidget(self.default_area, self)
                    self.setFloating(True)
                else:
                    self.main_window.addDockWidget(area, self)
            except AttributeError:
                self.main_window.addDockWidget(self.default_area, self)
        else:
            self.main_window.addDockWidget(self.default_area, self)

    def _restore_settings(self):
        pos = self.config["pos"]
        size = self.config["size"]
        if pos and size:
            self.setGeometry(pos[0], pos[1], size[0], size[1])

        self.setVisible(self.config.get("visible", True))

        self._restore_area()

        if size:
            self.main_window.resizeDocks([self], [size[0]], Qt.Horizontal)
            self.main_window.resizeDocks([self], [size[1]], Qt.Vertical)
