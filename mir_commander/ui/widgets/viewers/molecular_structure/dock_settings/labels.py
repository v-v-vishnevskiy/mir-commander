from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout

from mir_commander.ui.utils.widget import GroupBox, Label

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer
    from .settings import Settings


class Labels(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(self.tr("Labels"))

        self._settings = parent

        # Size slider
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(100)
        self.size_slider.setSingleStep(1)
        self.size_slider.setSliderPosition(1)
        self.size_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.size_slider.setTickInterval(25)
        self.size_slider.valueChanged.connect(self.size_slider_value_changed_handler)

        self.size_double_spinbox = QDoubleSpinBox()
        self.size_double_spinbox.setRange(1.0, 100.0)
        self.size_double_spinbox.setSingleStep(1.0)
        self.size_double_spinbox.setDecimals(0)
        self.size_double_spinbox.setValue(1.0)
        self.size_double_spinbox.valueChanged.connect(self.size_double_spinbox_value_changed_handler)

        # Offset slider
        self.offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.offset_slider.setMinimum(101)  # 1.01 * 100
        self.offset_slider.setMaximum(500)  # 5.0 * 100
        self.offset_slider.setSingleStep(10)  # 0.1 * 100
        self.offset_slider.setSliderPosition(int(1.01 * 100))
        self.offset_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.offset_slider.setTickInterval(50)
        self.offset_slider.valueChanged.connect(self.offset_slider_value_changed_handler)

        self.offset_double_spinbox = QDoubleSpinBox()
        self.offset_double_spinbox.setRange(1.01, 5.0)
        self.offset_double_spinbox.setSingleStep(0.1)
        self.offset_double_spinbox.setDecimals(2)
        self.offset_double_spinbox.setValue(1.01)
        self.offset_double_spinbox.valueChanged.connect(self.offset_double_spinbox_value_changed_handler)

        # Size layout
        size_layout = QGridLayout()
        label = Label(Label.tr("Size:"), parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_layout.addWidget(label, 0, 0, 1, 3)
        size_layout.addWidget(self.size_slider, 1, 0, 1, 3)
        size_layout.addWidget(self.size_double_spinbox, 1, 4)
        label = Label("1", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        size_layout.addWidget(label, 2, 0)
        label = Label("50", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        size_layout.addWidget(label, 2, 1)
        label = Label("100", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        size_layout.addWidget(label, 2, 2)

        # Offset layout
        offset_layout = QGridLayout()
        label = Label(Label.tr("Offset:"), parent)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        offset_layout.addWidget(label, 0, 0, 1, 3)
        offset_layout.addWidget(self.offset_slider, 1, 0, 1, 3)
        offset_layout.addWidget(self.offset_double_spinbox, 1, 4)
        label = Label("1.01", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        offset_layout.addWidget(label, 2, 0)
        label = Label("2.0", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        offset_layout.addWidget(label, 2, 1)
        label = Label("3.0", parent)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        offset_layout.addWidget(label, 2, 2)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(size_layout)
        self.main_layout.addLayout(offset_layout)
        self.setLayout(self.main_layout)

    def update_values(self, viewer: "MolecularStructureViewer"):
        self.size_slider.setValue(viewer.ac_viewer.config.atom_label.size)
        self.size_double_spinbox.setValue(viewer.ac_viewer.config.atom_label.size)

        self.offset_slider.setValue(int(viewer.ac_viewer.config.atom_label.offset * 100))
        self.offset_double_spinbox.setValue(viewer.ac_viewer.config.atom_label.offset)

    def apply_settings(self, viewers: list["MolecularStructureViewer"]):
        for viewer in viewers:
            viewer.ac_viewer.set_label_size_for_all_atoms(size=self.size_slider.value())
            viewer.ac_viewer.set_label_offset_for_all_atoms(offset=self.offset_slider.value() / 100)

    @Slot()
    def size_slider_value_changed_handler(self, i: int):
        self.size_double_spinbox.setValue(i)
        for viewer in self._settings.viewers:
            viewer.ac_viewer.set_label_size_for_all_atoms(size=i)

    @Slot()
    def size_double_spinbox_value_changed_handler(self, value: int):
        self.size_slider.setValue(value)

    @Slot()
    def offset_slider_value_changed_handler(self, i: int):
        self.offset_double_spinbox.setValue(i / 100)
        for viewer in self._settings.viewers:
            viewer.ac_viewer.set_label_offset_for_all_atoms(offset=i / 100)

    @Slot()
    def offset_double_spinbox_value_changed_handler(self, value: float):
        self.offset_slider.setValue(int(value * 100))
