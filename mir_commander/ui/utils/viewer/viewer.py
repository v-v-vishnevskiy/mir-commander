from pydantic import BaseModel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.viewer.viewer_settings import ViewerSettings


class Viewer(QMdiSubWindow):
    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
    settings: type[ViewerSettings] | None = None

    def __init__(self, parent: QWidget, item: QStandardItem, app_config: AppConfig):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.item = item
        self.app_config = app_config

    def get_config(self) -> BaseModel:
        raise NotImplementedError("This method should be implemented in the subclass")
