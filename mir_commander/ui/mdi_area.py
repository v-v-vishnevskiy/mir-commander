from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from .widgets.viewers.config import ViewersConfig


class MdiArea(QMdiArea):
    added_viewer = Signal(Any)

    def __init__(self, parent: QWidget, viewers_config: ViewersConfig):
        super().__init__(parent)
        self._viewers_config = viewers_config

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

    def open_viewer(self, item: QStandardItem, viewer_cls: type[QWidget], kwargs: dict[str, Any]):
        for sub_window in self.subWindowList():
            # checking if viewer for this item already opened
            if id(sub_window.widget().item) == id(item):
                self.setActiveSubWindow(sub_window)
                viewer = sub_window.widget()
                break
        else:
            sub_window = QMdiSubWindow(self)
            sub_window.setAttribute(Qt.WA_DeleteOnClose)
            viewer = viewer_cls(parent=sub_window, config=self._viewers_config, item=item, **kwargs)
            self.added_viewer.emit(viewer)
            sub_window.setWidget(viewer)
            self.addSubWindow(sub_window)
        viewer.showNormal()
