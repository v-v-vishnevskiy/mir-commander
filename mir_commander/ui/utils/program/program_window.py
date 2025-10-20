from typing import TYPE_CHECKING

from pydantic import BaseModel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QMdiSubWindow, QWidget

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.widget import Translator, TrString

from .program_control_panel import ProgramControlPanel

if TYPE_CHECKING:
    from mir_commander.ui.widgets.docks.project_dock.items import TreeItem


class ProgramWindow(QMdiSubWindow):
    short_msg_signal = Signal(str)
    long_msg_signal = Signal(str)
    control_panel_cls: type[ProgramControlPanel] | None = None
    name: TrString

    def __init__(
        self, parent: QWidget, item: "TreeItem", app_config: AppConfig, control_panel: ProgramControlPanel | None
    ):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setGraphicsEffect(
            QGraphicsDropShadowEffect(parent=self, blurRadius=100, color=QColor(0, 0, 0, 128), xOffset=0, yOffset=0)
        )

        self.item = item
        self.app_config = app_config
        self.control_panel = control_panel

    @classmethod
    def get_name(cls) -> str:
        return Translator.translate(cls.name)

    def get_config(self) -> BaseModel:
        raise NotImplementedError("This method should be implemented in the subclass")
