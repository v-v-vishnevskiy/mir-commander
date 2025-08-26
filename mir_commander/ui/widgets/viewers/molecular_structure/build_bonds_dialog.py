from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDialogButtonBox, QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout

from mir_commander.ui.utils.widget import Dialog, Label

if TYPE_CHECKING:
    from .atomic_coordinates_viewer import AtomicCoordinatesViewer


class BuildBondsDialog(Dialog):
    def __init__(self, current_tol: float, parent: "AtomicCoordinatesViewer"):
        super().__init__(parent)

        self.ac_viewer = parent
        self.current_tol = current_tol

        self.setWindowTitle(self.tr("Build bonds"))

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(-100)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)
        self.slider.setSliderPosition(int(self.current_tol * 100.0))
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(100)
        self.slider.valueChanged.connect(self.slider_value_changed_handler)

        self.double_spinbox = QDoubleSpinBox()
        self.double_spinbox.setRange(-1.00, 1.00)
        self.double_spinbox.setSingleStep(0.05)
        self.double_spinbox.setDecimals(2)
        self.double_spinbox.setValue(self.current_tol)
        self.double_spinbox.valueChanged.connect(self.double_spinbox_value_changed_handler)

        slider_layout = QGridLayout()
        label = Label(Label.tr("Threshold for bond detection:"), self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slider_layout.addWidget(label, 0, 0, 1, 3)
        slider_layout.addWidget(self.slider, 1, 0, 1, 3)
        slider_layout.addWidget(self.double_spinbox, 1, 4)
        label = Label("-1.0", self)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        slider_layout.addWidget(label, 2, 0)
        label = Label("0.0", self)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        slider_layout.addWidget(label, 2, 1)
        label = Label("1.0", self)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        slider_layout.addWidget(label, 2, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(slider_layout)

        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)

    @Slot()
    def slider_value_changed_handler(self, i: int):
        self.current_tol = float(i) / 100.0
        self.double_spinbox.setValue(self.current_tol)
        self.ac_viewer.rebuild_bonds(tol=self.current_tol)

    @Slot()
    def double_spinbox_value_changed_handler(self, value: float):
        self.slider.setValue(int(value * 100.0))
