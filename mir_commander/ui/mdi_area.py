from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from .widgets.docks import ViewerSettingsDock
from .widgets.viewers.base import BaseViewer
from .widgets.viewers.config import ViewersConfig


class MdiArea(QMdiArea):
    added_viewer_signal = Signal(BaseViewer)

    def __init__(self, parent: QWidget, viewer_settings_dock: ViewerSettingsDock, viewers_config: ViewersConfig):
        super().__init__(parent)
        self._viewer_settings_dock = viewer_settings_dock
        self._viewers_config = viewers_config

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.subWindowActivated.connect(self.sub_window_activated_handler)

    def open_viewer(self, item: QStandardItem, viewer_cls: type[BaseViewer], kwargs: dict[str, Any]):
        for sub_window in self.subWindowList():
            # checking if viewer for this item already opened
            if id(sub_window.widget().item) == id(item):
                self.setActiveSubWindow(sub_window)
                viewer = sub_window.widget()
                break
        else:
            sub_window = QMdiSubWindow(self)
            sub_window.setAttribute(Qt.WA_DeleteOnClose)
            viewer = viewer_cls(
                parent=sub_window,
                config=self._viewers_config.get_viewer_config(viewer_cls),
                item=item,
                **kwargs,
            )
            self.added_viewer_signal.emit(viewer)
            sub_window.setWidget(viewer)
            self.addSubWindow(sub_window)
        viewer.showNormal()

    def sub_window_activated_handler(self, window: QMdiSubWindow):
        self._viewer_settings_dock.setWidget(window.widget().settings if window is not None else None)
