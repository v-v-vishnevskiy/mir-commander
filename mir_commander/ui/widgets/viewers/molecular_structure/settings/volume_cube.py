from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout

from mir_commander.ui.utils.widget import GroupBox, Label

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer
    from .settings import Settings


class VolumeCube(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(self.tr("Volume Cube"))

        self._settings = parent

        # Size slider (scaled by 100 to handle 0.01 step with integer slider)
        self.value_slider = QSlider(Qt.Orientation.Horizontal)
        self.value_slider.setMinimum(-500)  # -5.0 * 100
        self.value_slider.setMaximum(500)  # 5.0 * 100
        self.value_slider.setSingleStep(1)  # 0.01 * 100
        self.value_slider.setSliderPosition(0)  # 0.0 * 100
        self.value_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.value_slider.setTickInterval(250)  # 2.5 * 100
        self.value_slider.valueChanged.connect(self.value_slider_value_changed_handler)

        self.value_double_spinbox = QDoubleSpinBox()
        self.value_double_spinbox.setRange(-5.0, 5.0)
        self.value_double_spinbox.setSingleStep(0.01)
        self.value_double_spinbox.setDecimals(2)
        self.value_double_spinbox.setValue(0.0)
        self.value_double_spinbox.valueChanged.connect(self.value_double_spinbox_value_changed_handler)

        # Value layout
        size_layout = QGridLayout()
        label = Label(Label.tr("Value:"), parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_layout.addWidget(label, 0, 0, 1, 3)
        size_layout.addWidget(self.value_slider, 1, 0, 1, 3)
        size_layout.addWidget(self.value_double_spinbox, 1, 4)
        label = Label("-5.0", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        size_layout.addWidget(label, 2, 0)
        label = Label("0.0", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        size_layout.addWidget(label, 2, 1)
        label = Label("5.0", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        size_layout.addWidget(label, 2, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(size_layout)
        self.setLayout(self.main_layout)

    def update_values(self, viewer: "MolecularStructureViewer"):
        self.value_slider.setValue(0)
        self.value_double_spinbox.setValue(0)

    def apply_settings(self, viewers: list["MolecularStructureViewer"]):
        for viewer in viewers:
            # Convert slider value to actual float value
            actual_value = self.value_slider.value() / 100.0
            viewer.visualizer.build_volume_cube(value=actual_value)

    @Slot()
    def value_slider_value_changed_handler(self, i: int):
        # Convert slider value (scaled by 100) to actual float value
        actual_value = i / 100.0
        self.value_double_spinbox.setValue(actual_value)
        for viewer in self._settings.viewers:
            viewer.visualizer.build_volume_cube(value=actual_value)

    @Slot()
    def value_double_spinbox_value_changed_handler(self, value: float):
        # Convert float value to slider value (scaled by 100)
        slider_value = int(value * 100)
        self.value_slider.setValue(slider_value)
