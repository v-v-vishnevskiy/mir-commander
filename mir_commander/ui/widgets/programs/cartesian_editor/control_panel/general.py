from typing import TYPE_CHECKING

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QSpinBox, QWidget

from mir_commander.ui.utils.widget import GridLayout, Label

if TYPE_CHECKING:
    from ..program import CartesianEditor
    from .control_panel import ControlPanel


class General(QWidget):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__(parent=control_panel)

        self._control_panel = control_panel

        layout = GridLayout(self)

        self._decimals_spinbox = QSpinBox()
        self._decimals_spinbox.setRange(1, 15)
        self._decimals_spinbox.setValue(6)
        self._decimals_spinbox.valueChanged.connect(self._decimals_spinbox_value_changed_handler)

        layout.addWidget(Label(Label.tr("Decimals:")), 0, 0)
        layout.addWidget(self._decimals_spinbox, 0, 1)

        self.setLayout(layout)

    def _decimals_spinbox_value_changed_handler(self, value: int):
        for program in self._control_panel.opened_programs:
            program.set_decimals(value)

    def update_values(self, program: "CartesianEditor"):
        with QSignalBlocker(self._decimals_spinbox):
            self._decimals_spinbox.setValue(program.decimals)
