from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGridLayout, QVBoxLayout

from mir_commander.ui.utils.widget import CheckBox, GroupBox

if TYPE_CHECKING:
    from .settings import Settings


class CoordinateAxes(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(text=self.tr("Coordinate Axes"), parent=parent)

        self._settings = parent

        # Value layout
        value_layout = QGridLayout()

        self._show_checkbox = CheckBox(CheckBox.tr("Show"))
        self._show_checkbox.setChecked(False)
        self._show_checkbox.toggled.connect(self._show_checkbox_toggled_handler)

        value_layout.addWidget(self._show_checkbox, 0, 0)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(value_layout)
        self.setLayout(self.main_layout)

    def _show_checkbox_toggled_handler(self, checked: bool):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_visible_coordinate_axes(checked)
