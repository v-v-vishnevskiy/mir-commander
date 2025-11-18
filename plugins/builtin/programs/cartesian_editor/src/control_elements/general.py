from typing import TYPE_CHECKING

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QGridLayout, QLabel, QSpinBox

from ....program import ControlBlock

if TYPE_CHECKING:
    from ..control_panel import ControlPanel
    from ..program import Program


class General(ControlBlock):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()

        self._control_panel = control_panel

        layout = QGridLayout(self)

        self._decimals_spinbox = QSpinBox()
        self._decimals_spinbox.setRange(1, 15)
        self._decimals_spinbox.setValue(6)
        self._decimals_spinbox.valueChanged.connect(self._control_panel.set_decimals)

        layout.addWidget(QLabel(self.tr("Decimals:")), 0, 0)
        layout.addWidget(self._decimals_spinbox, 0, 1)

        self.setLayout(layout)

    def update_values(self, program: "Program"):
        with QSignalBlocker(self._decimals_spinbox):
            self._decimals_spinbox.setValue(program.decimals)
