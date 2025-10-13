from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider

from mir_commander.ui.utils.widget import Label, TrString


def add_slider(
    layout: QGridLayout,
    row: int,
    text: TrString,
    min_value: float,
    max_value: float,
    single_step: float,
    default_value: float,
    factor: int = 1,
    decimals: int = 0,
) -> tuple[QSlider, QDoubleSpinBox]:
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(int(min_value * factor), int(max_value * factor))
    slider.setSingleStep(1)
    slider.setSliderPosition(int(default_value * factor))

    double_spinbox = QDoubleSpinBox()
    double_spinbox.setRange(min_value, max_value)
    double_spinbox.setSingleStep(single_step)
    double_spinbox.setDecimals(decimals)
    double_spinbox.setValue(default_value)

    label = Label(text)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft)
    layout.addWidget(label, row, 0)
    layout.addWidget(slider, row, 1, 1, 3)
    layout.addWidget(double_spinbox, row, 4)

    return slider, double_spinbox
