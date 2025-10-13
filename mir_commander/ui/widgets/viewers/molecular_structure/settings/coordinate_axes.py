from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGridLayout, QVBoxLayout

from mir_commander.ui.utils.widget import CheckBox, GroupBox, Label

from .utils import add_slider

if TYPE_CHECKING:
    from .settings import Settings


class CoordinateAxes(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(text=self.tr("Coordinate Axes"), parent=parent)

        self._settings = parent

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self._add_checkboxes())
        self.main_layout.addLayout(self._add_sliders())
        self.setLayout(self.main_layout)

    def _add_checkboxes(self) -> QGridLayout:
        layout = QGridLayout()

        visibility_checkbox = CheckBox(CheckBox.tr("Visible"))
        visibility_checkbox.setChecked(False)
        visibility_checkbox.toggled.connect(self._visibility_checkbox_toggled_handler)

        labels_visibility_checkbox = CheckBox(CheckBox.tr("Labels"))
        labels_visibility_checkbox.setChecked(True)
        labels_visibility_checkbox.toggled.connect(self._labels_visibility_checkbox_toggled_handler)

        full_length_checkbox = CheckBox(CheckBox.tr("Full Length"))
        full_length_checkbox.setChecked(False)
        full_length_checkbox.toggled.connect(self._full_length_checkbox_toggled_handler)

        center_checkbox = CheckBox(CheckBox.tr("Center"))
        center_checkbox.setChecked(False)
        center_checkbox.toggled.connect(self._center_checkbox_toggled_handler)

        layout.addWidget(visibility_checkbox, 0, 0)
        layout.addWidget(labels_visibility_checkbox, 0, 1)
        layout.addWidget(full_length_checkbox, 1, 0)
        layout.addWidget(center_checkbox, 1, 1)

        return layout

    def _add_sliders(self) -> QGridLayout:
        layout = QGridLayout()

        self.length_slider, self.length_double_spinbox = add_slider(
            layout=layout,
            row=0,
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

        self.thickness_slider, self.thickness_double_spinbox = add_slider(
            layout=layout,
            row=1,
            text=Label.tr("Thickness:"),
            min_value=0.01,
            max_value=1.0,
            single_step=0.01,
            default_value=0.03,
            factor=100,
            decimals=2,
        )
        self.thickness_slider.valueChanged.connect(self.thickness_slider_value_changed_handler)
        self.thickness_double_spinbox.valueChanged.connect(self.thickness_double_spinbox_value_changed_handler)

        self.label_size_slider, self.label_size_double_spinbox = add_slider(
            layout=layout,
            row=2,
            text=Label.tr("Label Size:"),
            min_value=1,
            max_value=500,
            single_step=1,
            default_value=8,
        )
        self.label_size_slider.valueChanged.connect(self.label_size_slider_value_changed_handler)
        self.label_size_double_spinbox.valueChanged.connect(self.label_size_double_spinbox_value_changed_handler)

        return layout

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

    def thickness_slider_value_changed_handler(self, i: int):
        self.thickness_double_spinbox.setValue(i / 100)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_thickness(i / 100)

    def thickness_double_spinbox_value_changed_handler(self, value: float):
        self.thickness_slider.setValue(int(value * 100))

    def label_size_slider_value_changed_handler(self, i: int):
        self.label_size_double_spinbox.setValue(i)
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axes_labels_size(i)

    def label_size_double_spinbox_value_changed_handler(self, value: int):
        self.label_size_slider.setValue(value)
