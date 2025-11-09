from typing import TYPE_CHECKING

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QSpinBox

from mir_commander.ui.sdk.program_control_panel import ControlComponent
from mir_commander.ui.sdk.widget import GridLayout, Label

if TYPE_CHECKING:
    from ..control_panel import ControlPanel
    from ..program import Program


class General(ControlComponent):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()

        self._control_panel = control_panel

        layout = GridLayout(self)

        self._decimals_spinbox = QSpinBox()
        self._decimals_spinbox.setRange(1, 15)
        self._decimals_spinbox.setValue(6)
        self._decimals_spinbox.valueChanged.connect(self._control_panel.set_decimals)

        layout.addWidget(Label(Label.tr("Decimals:")), 0, 0)
        layout.addWidget(self._decimals_spinbox, 0, 1)

        self.setLayout(layout)

    def update_values(self, program: "Program"):
        with QSignalBlocker(self._decimals_spinbox):
            self._decimals_spinbox.setValue(program.decimals)
