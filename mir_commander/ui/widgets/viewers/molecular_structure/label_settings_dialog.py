from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDialogButtonBox, QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout, QWidget

from mir_commander.ui.utils.widget import Dialog, Label


class LabelSettingsDialog(Dialog):
    def __init__(self, current_size: int, current_offset: float, viewer: QWidget):
        super().__init__(viewer)

        self.viewer_widget = viewer
        self.current_size = current_size
        self.current_offset = current_offset

        self.setWindowTitle(self.tr("Label settings"))

        # Size slider
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setSingleStep(1)
        self.size_slider.setSliderPosition(self.current_size)
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        self.size_slider.setTickInterval(25)
        self.size_slider.valueChanged.connect(self.size_slider_value_changed_handler)

        self.size_double_spinbox = QDoubleSpinBox()
        self.size_double_spinbox.setRange(1.0, 100.0)
        self.size_double_spinbox.setSingleStep(1.0)
        self.size_double_spinbox.setDecimals(0)
        self.size_double_spinbox.setValue(self.current_size)
        self.size_double_spinbox.valueChanged.connect(self.size_double_spinbox_value_changed_handler)

        # Offset slider
        self.offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_slider.setMinimum(101)  # 1.01 * 100
        self.offset_slider.setMaximum(500)  # 5.0 * 100
        self.offset_slider.setSingleStep(10)  # 0.1 * 100
        self.offset_slider.setSliderPosition(int(self.current_offset * 100))
        self.offset_slider.setTickPosition(QSlider.TicksBelow)
        self.offset_slider.setTickInterval(50)
        self.offset_slider.valueChanged.connect(self.offset_slider_value_changed_handler)

        self.offset_double_spinbox = QDoubleSpinBox()
        self.offset_double_spinbox.setRange(1.01, 5.0)
        self.offset_double_spinbox.setSingleStep(0.1)
        self.offset_double_spinbox.setDecimals(2)
        self.offset_double_spinbox.setValue(self.current_offset)
        self.offset_double_spinbox.valueChanged.connect(self.offset_double_spinbox_value_changed_handler)

        # Size layout
        size_layout = QGridLayout()
        label = Label(Label.tr("Label size:"), self)
        label.setAlignment(Qt.AlignCenter)
        size_layout.addWidget(label, 0, 0, 1, 3)
        size_layout.addWidget(self.size_slider, 1, 0, 1, 3)
        size_layout.addWidget(self.size_double_spinbox, 1, 4)
        label = Label("1", self)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        size_layout.addWidget(label, 2, 0)
        label = Label("50", self)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        size_layout.addWidget(label, 2, 1)
        label = Label("100", self)
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        size_layout.addWidget(label, 2, 2)

        # Offset layout
        offset_layout = QGridLayout()
        label = Label(Label.tr("Label offset:"), self)
        label.setAlignment(Qt.AlignCenter)
        offset_layout.addWidget(label, 0, 0, 1, 3)
        offset_layout.addWidget(self.offset_slider, 1, 0, 1, 3)
        offset_layout.addWidget(self.offset_double_spinbox, 1, 4)
        label = Label("1.01", self)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        offset_layout.addWidget(label, 2, 0)
        label = Label("2.0", self)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        offset_layout.addWidget(label, 2, 1)
        label = Label("3.0", self)
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        offset_layout.addWidget(label, 2, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(size_layout)
        self.main_layout.addLayout(offset_layout)

        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)

    @Slot()
    def size_slider_value_changed_handler(self, i: int):
        self.current_size = i
        self.size_double_spinbox.setValue(self.current_size)
        self.viewer_widget.set_label_size_for_all_atoms(size=self.current_size)

    @Slot()
    def size_double_spinbox_value_changed_handler(self, value: int):
        self.current_size = value
        self.size_slider.setValue(self.current_size)

    @Slot()
    def offset_slider_value_changed_handler(self, i: int):
        self.current_offset = i / 100.0
        self.offset_double_spinbox.setValue(self.current_offset)
        self.viewer_widget.set_label_offset_for_all_atoms(offset=self.current_offset)

    @Slot()
    def offset_double_spinbox_value_changed_handler(self, value: float):
        self.current_offset = value
        self.offset_slider.setValue(int(self.current_offset * 100))
