from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.viewer import Viewer

from .widgets.docks.viewer_settings_dock import ViewerSettingsDock


class MdiArea(QMdiArea):
    opened_viewer_signal = Signal(Viewer)

    def __init__(self, parent: QWidget, viewer_settings_dock: ViewerSettingsDock, app_config: AppConfig):
        super().__init__(parent)
        self._viewer_settings_dock = viewer_settings_dock
        self._app_config = app_config

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.subWindowActivated.connect(self.sub_window_activated_handler)

    def open_viewer(self, item: QStandardItem, viewer_cls: type[Viewer], kwargs: dict[str, Any]):
        for viewer in self.subWindowList():
            # checking if viewer for this item already opened
            if isinstance(viewer, viewer_cls) and id(viewer.item) == id(item):
                self.setActiveSubWindow(viewer)
                break
        else:
            self._viewer_settings_dock.add_viewer_settings_widget(viewer_cls)
            viewer = viewer_cls(
                parent=self,
                app_config=self._app_config,
                item=item,
                **kwargs,
            )
            self.opened_viewer_signal.emit(viewer)
            self.addSubWindow(viewer)
        viewer.show()

    def sub_window_activated_handler(self, window: None | QMdiSubWindow):
        viewers = []
        for viewer in self.subWindowList():
            viewers.append(viewer)
        self._viewer_settings_dock.update_viewers_list(viewers)
        self._viewer_settings_dock.set_viewer_settings_widget(window)
