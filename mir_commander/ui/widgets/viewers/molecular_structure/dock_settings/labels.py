from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout, QWidget

from mir_commander.ui.utils.widget import GroupBox, Label

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer


class Labels(GroupBox):
    def __init__(self, parent: QWidget, viewer: "MolecularStructureViewer"):
        super().__init__(GroupBox.tr("Labels"))

        self._viewer = viewer

        # Size slider
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setSingleStep(1)
        self.size_slider.setSliderPosition(self._viewer.config.atom_label.size)
        self.size_slider.setTickPosition(QSlider.TicksBelow)
        self.size_slider.setTickInterval(25)
        self.size_slider.valueChanged.connect(self.size_slider_value_changed_handler)

        self.size_double_spinbox = QDoubleSpinBox()
        self.size_double_spinbox.setRange(1.0, 100.0)
        self.size_double_spinbox.setSingleStep(1.0)
        self.size_double_spinbox.setDecimals(0)
        self.size_double_spinbox.setValue(self._viewer.config.atom_label.size)
        self.size_double_spinbox.valueChanged.connect(self.size_double_spinbox_value_changed_handler)

        # Offset slider
        self.offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_slider.setMinimum(101)  # 1.01 * 100
        self.offset_slider.setMaximum(500)  # 5.0 * 100
        self.offset_slider.setSingleStep(10)  # 0.1 * 100
        self.offset_slider.setSliderPosition(int(self._viewer.config.atom_label.offset * 100))
        self.offset_slider.setTickPosition(QSlider.TicksBelow)
        self.offset_slider.setTickInterval(50)
        self.offset_slider.valueChanged.connect(self.offset_slider_value_changed_handler)

        self.offset_double_spinbox = QDoubleSpinBox()
        self.offset_double_spinbox.setRange(1.01, 5.0)
        self.offset_double_spinbox.setSingleStep(0.1)
        self.offset_double_spinbox.setDecimals(2)
        self.offset_double_spinbox.setValue(self._viewer.config.atom_label.offset)
        self.offset_double_spinbox.valueChanged.connect(self.offset_double_spinbox_value_changed_handler)

        # Size layout
        size_layout = QGridLayout()
        label = Label(Label.tr("Size:"), parent)
        label.setAlignment(Qt.AlignCenter)
        size_layout.addWidget(label, 0, 0, 1, 3)
        size_layout.addWidget(self.size_slider, 1, 0, 1, 3)
        size_layout.addWidget(self.size_double_spinbox, 1, 4)
        label = Label("1", parent)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        size_layout.addWidget(label, 2, 0)
        label = Label("50", parent)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        size_layout.addWidget(label, 2, 1)
        label = Label("100", parent)
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        size_layout.addWidget(label, 2, 2)

        # Offset layout
        offset_layout = QGridLayout()
        label = Label(Label.tr("Offset:"), parent)
        label.setAlignment(Qt.AlignCenter)
        offset_layout.addWidget(label, 0, 0, 1, 3)
        offset_layout.addWidget(self.offset_slider, 1, 0, 1, 3)
        offset_layout.addWidget(self.offset_double_spinbox, 1, 4)
        label = Label("1.01", parent)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        offset_layout.addWidget(label, 2, 0)
        label = Label("2.0", parent)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        offset_layout.addWidget(label, 2, 1)
        label = Label("3.0", parent)
        label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        offset_layout.addWidget(label, 2, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(size_layout)
        self.main_layout.addLayout(offset_layout)
        self.setLayout(self.main_layout)

    @Slot()
    def size_slider_value_changed_handler(self, i: int):
        self._viewer.config.atom_label.size = i
        self.size_double_spinbox.setValue(self._viewer.config.atom_label.size)
        self._viewer.set_label_size_for_all_atoms(size=self._viewer.config.atom_label.size)

    @Slot()
    def size_double_spinbox_value_changed_handler(self, value: int):
        self._viewer.config.atom_label.size = value
        self.size_slider.setValue(self._viewer.config.atom_label.size)

    @Slot()
    def offset_slider_value_changed_handler(self, i: int):
        self._viewer.config.atom_label.offset = i / 100.0
        self.offset_double_spinbox.setValue(self._viewer.config.atom_label.offset)
        self._viewer.set_label_offset_for_all_atoms(offset=self._viewer.config.atom_label.offset)

    @Slot()
    def offset_double_spinbox_value_changed_handler(self, value: float):
        self._viewer.config.atom_label.offset = value
        self.offset_slider.setValue(int(self._viewer.config.atom_label.offset * 100))
