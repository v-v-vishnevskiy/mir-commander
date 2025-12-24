from typing import TYPE_CHECKING

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout

from mir_commander.core.graphics.utils import color4f_to_qcolor, qcolor_to_color4f
from mir_commander.ui.sdk.widget import ColorButton

from ...program import ControlBlock

if TYPE_CHECKING:
    from ..control_panel import ControlPanel
    from ..program import Program


class Appearance(ControlBlock):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()

        self._control_panel = control_panel

        layout = QVBoxLayout(self)

        bg_color_layout = QHBoxLayout()
        bg_color_layout.addWidget(QLabel(self.tr("Background color:"), self))
        self._bg_color_button = ColorButton(QColor(255, 255, 255), alpha=False)
        self._bg_color_button.color_changed.connect(self._bg_color_button_color_changed_handler)
        bg_color_layout.addWidget(self._bg_color_button)
        bg_color_layout.addStretch(1)

        layout.addLayout(bg_color_layout)
        self.setLayout(layout)

    def _bg_color_button_color_changed_handler(self, color: QColor):
        self._control_panel.program_action_signal.emit("appearance.set_bg_color", {"color": qcolor_to_color4f(color)})

    def update_values(self, program: "Program"):
        color = *program.visualizer.background_color[:3], 1.0
        self._bg_color_button.set_color(color4f_to_qcolor(color))
