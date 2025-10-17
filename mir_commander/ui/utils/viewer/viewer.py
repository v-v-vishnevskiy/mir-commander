from pydantic import BaseModel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.viewer.viewer_settings import ViewerSettings
from mir_commander.ui.utils.widget import Translator, TrString


class Viewer(QMdiSubWindow):
    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
    settings: type[ViewerSettings] | None = None
    name: TrString

    def __init__(
        self, parent: QWidget, item: QStandardItem, app_config: AppConfig, settings_widget: ViewerSettings | None
    ):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.item = item
        self.app_config = app_config
        self.settings_widget = settings_widget

    @classmethod
    def get_name(cls) -> str:
        return Translator.translate(cls.name)

    def get_config(self) -> BaseModel:
        raise NotImplementedError("This method should be implemented in the subclass")
