from pydantic import BaseModel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.widget import Translator, TrString

from .program_control_panel import ProgramControlPanel


class ProgramWindow(QMdiSubWindow):
    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
    control_panel_cls: type[ProgramControlPanel] | None = None
    name: TrString

    def __init__(
        self, parent: QWidget, item: QStandardItem, app_config: AppConfig, control_panel: ProgramControlPanel | None
    ):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.item = item
        self.app_config = app_config
        self.control_panel = control_panel

    @classmethod
    def get_name(cls) -> str:
        return Translator.translate(cls.name)

    def get_config(self) -> BaseModel:
        raise NotImplementedError("This method should be implemented in the subclass")
