from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider

from mir_commander.ui.sdk.widget import Label, TrString


def add_slider(
    layout: QGridLayout,
    row: int,
    text: TrString,
    min_value: float,
    max_value: float,
    label_tooltip: TrString | None = None,
    single_step: float = 1.0,
    factor: int = 1,
    decimals: int = 0,
    default_value: float = 0.0,
) -> tuple[QSlider, QDoubleSpinBox]:
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(int(min_value * factor), int(max_value * factor))
    slider.setSingleStep(int(single_step * factor))
    slider.setValue(int(default_value * factor))

    double_spinbox = QDoubleSpinBox()
    double_spinbox.setRange(min_value, max_value)
    double_spinbox.setSingleStep(single_step)
    double_spinbox.setDecimals(decimals)
    double_spinbox.setValue(default_value)

    label = Label(text)
    if label_tooltip is not None:
        label.setToolTip(label_tooltip)
    layout.addWidget(label, row, 0)
    layout.addWidget(slider, row, 1)
    layout.addWidget(double_spinbox, row, 2)

    return slider, double_spinbox
