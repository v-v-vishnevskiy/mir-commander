from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDialogButtonBox, QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout, QWidget

from mir_commander.ui.utils.widget import Dialog, Label


class LabelSettingsDialog(Dialog):
    def __init__(self, current_size: int, viewer: QWidget):
        super().__init__(viewer)

        self.viewer_widget = viewer
        self.current_size = current_size

        self.setWindowTitle(self.tr("Label size settings"))

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)
        self.slider.setSliderPosition(self.current_size)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(25)
        self.slider.valueChanged.connect(self.slider_value_changed_handler)

        self.double_spinbox = QDoubleSpinBox()
        self.double_spinbox.setRange(1.0, 100.0)
        self.double_spinbox.setSingleStep(1.0)
        self.double_spinbox.setDecimals(0)
        self.double_spinbox.setValue(self.current_size)
        self.double_spinbox.valueChanged.connect(self.double_spinbox_value_changed_handler)

        slider_layout = QGridLayout()
        label = Label(Label.tr("Label size:"), self)
        label.setAlignment(Qt.AlignCenter)
        slider_layout.addWidget(label, 0, 0, 1, 3)
        slider_layout.addWidget(self.slider, 1, 0, 1, 3)
        slider_layout.addWidget(self.double_spinbox, 1, 4)
        label = Label("1", self)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        slider_layout.addWidget(label, 2, 0)
        label = Label("50", self)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        slider_layout.addWidget(label, 2, 1)
        label = Label("100", self)
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        slider_layout.addWidget(label, 2, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(slider_layout)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)

    @Slot()
    def slider_value_changed_handler(self, i: int):
        self.current_size = i
        self.double_spinbox.setValue(self.current_size)
        self.viewer_widget.set_label_size_for_all_atoms(size=self.current_size)

    @Slot()
    def double_spinbox_value_changed_handler(self, value: int):
        self.current_size = value
        self.slider.setValue(self.current_size)
