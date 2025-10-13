from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout

from mir_commander.ui.utils.widget import CheckBox, GroupBox, Label, TrString

if TYPE_CHECKING:
    from .settings import Settings


class CoordinateAxes(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(text=self.tr("Coordinate Axes"), parent=parent)

        self._settings = parent

        # Value layout
        checkboxes_layout = QGridLayout()

        self._visibility_checkbox = CheckBox(CheckBox.tr("Visible"))
        self._visibility_checkbox.setChecked(False)
        self._visibility_checkbox.toggled.connect(self._visibility_checkbox_toggled_handler)

        self._labels_visibility_checkbox = CheckBox(CheckBox.tr("Labels"))
        self._labels_visibility_checkbox.setChecked(True)
        self._labels_visibility_checkbox.toggled.connect(self._labels_visibility_checkbox_toggled_handler)

        self._full_length_checkbox = CheckBox(CheckBox.tr("Full Length"))
        self._full_length_checkbox.setChecked(False)
        self._full_length_checkbox.toggled.connect(self._full_length_checkbox_toggled_handler)

        self._center_checkbox = CheckBox(CheckBox.tr("Center"))
        self._center_checkbox.setChecked(False)
        self._center_checkbox.toggled.connect(self._center_checkbox_toggled_handler)

        length_layout, self.length_slider, self.length_double_spinbox = self._add_slider(
            text=Label.tr("Length:"),
            min_value=0.5,
            max_value=100.0,
            single_step=0.1,
            default_value=0.5,
            factor=100,
            decimals=1,
        )
        self.length_slider.valueChanged.connect(self.length_slider_value_changed_handler)
        self.length_double_spinbox.valueChanged.connect(self.length_double_spinbox_value_changed_handler)

        radius_layout, self.radius_slider, self.radius_double_spinbox = self._add_slider(
            text=Label.tr("Radius:"),
            min_value=0.01,
            max_value=1.0,
            single_step=0.01,
            default_value=0.03,
            factor=100,
            decimals=2,
        )
        self.radius_slider.valueChanged.connect(self.radius_slider_value_changed_handler)
        self.radius_double_spinbox.valueChanged.connect(self.radius_double_spinbox_value_changed_handler)

        label_size_layout, self.label_size_slider, self.label_size_double_spinbox = self._add_slider(
            text=Label.tr("Label Size:"),
            min_value=1,
            max_value=500,
            single_step=1,
            default_value=8,
            factor=1,
            decimals=0,
        )
        self.label_size_slider.valueChanged.connect(self.label_size_slider_value_changed_handler)
        self.label_size_double_spinbox.valueChanged.connect(self.label_size_double_spinbox_value_changed_handler)

        checkboxes_layout.addWidget(self._visibility_checkbox, 0, 0)
        checkboxes_layout.addWidget(self._labels_visibility_checkbox, 0, 1)
        checkboxes_layout.addWidget(self._full_length_checkbox, 1, 0)
        checkboxes_layout.addWidget(self._center_checkbox, 1, 1)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(checkboxes_layout)
        self.main_layout.addLayout(length_layout)
        self.main_layout.addLayout(radius_layout)
        self.main_layout.addLayout(label_size_layout)
        self.setLayout(self.main_layout)

    def _add_slider(
        self,
        text: TrString,
        min_value: float,
        max_value: float,
        single_step: float,
        default_value: float,
        factor: int,
        decimals: int = 0,
    ) -> tuple[QGridLayout, QSlider, QDoubleSpinBox]:
        length_slider = QSlider(Qt.Orientation.Horizontal)
        length_slider.setRange(int(min_value * factor), int(max_value * factor))
        length_slider.setSingleStep(1)
        length_slider.setSliderPosition(int(default_value * factor))
        length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        length_slider.setTickInterval(int(max_value * factor / 10))

        length_double_spinbox = QDoubleSpinBox()
        length_double_spinbox.setRange(min_value, max_value)
        length_double_spinbox.setSingleStep(single_step)
        length_double_spinbox.setDecimals(decimals)
        length_double_spinbox.setValue(default_value)

        length_layout = QGridLayout()
        label = Label(text, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        length_layout.addWidget(label, 0, 0, 1, 3)
        length_layout.addWidget(length_slider, 1, 0, 1, 3)
        length_layout.addWidget(length_double_spinbox, 1, 4)
        label = Label(str(min_value), self)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        length_layout.addWidget(label, 2, 0)
        label = Label(str(max_value / 2), self)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        length_layout.addWidget(label, 2, 1)
        label = Label(str(max_value), self)
        label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        length_layout.addWidget(label, 2, 2)

        return length_layout, length_slider, length_double_spinbox

    def _visibility_checkbox_toggled_handler(self, value: bool):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_visible(value)

    def _labels_visibility_checkbox_toggled_handler(self, value: bool):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_labels_visible(value)

    def _full_length_checkbox_toggled_handler(self, value: bool):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_full_length(value)

    def _center_checkbox_toggled_handler(self, value: bool):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_center(value)

    def length_slider_value_changed_handler(self, i: int):
        self.length_double_spinbox.setValue(i / 100)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_length(i / 100)

    def length_double_spinbox_value_changed_handler(self, value: float):
        self.length_slider.setValue(int(value * 100))

    def radius_slider_value_changed_handler(self, i: int):
        self.radius_double_spinbox.setValue(i / 100)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_radius(i / 100)

    def radius_double_spinbox_value_changed_handler(self, value: float):
        self.radius_slider.setValue(int(value * 100))

    def label_size_slider_value_changed_handler(self, i: int):
        self.label_size_double_spinbox.setValue(i)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_labels_size(i)

    def label_size_double_spinbox_value_changed_handler(self, value: int):
        self.label_size_slider.setValue(value)
