from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QLineEdit, QVBoxLayout

from mir_commander.ui.utils.opengl.utils import color4f_to_qcolor, qcolor_to_color4f
from mir_commander.ui.utils.widget import CheckBox, GroupBox, Label, PushButton, TrString

from .utils import ColorButton, add_slider

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer
    from .settings import Settings


class CoordinateAxes(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(text=self.tr("Coordinate Axes"), parent=parent)

        self._settings = parent

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self._add_checkboxes())
        self.main_layout.addLayout(self._add_sliders())
        self.main_layout.addLayout(self._add_axes())
        self.setLayout(self.main_layout)

    def _add_checkboxes(self) -> QGridLayout:
        layout = QGridLayout()

        self._visibility_checkbox = CheckBox(CheckBox.tr("Show"))
        self._visibility_checkbox.setChecked(False)
        self._visibility_checkbox.toggled.connect(self._visibility_checkbox_toggled_handler)

        self._labels_visibility_checkbox = CheckBox(CheckBox.tr("Labels"))
        self._labels_visibility_checkbox.setChecked(True)
        self._labels_visibility_checkbox.toggled.connect(self._labels_visibility_checkbox_toggled_handler)

        self._full_length_checkbox = CheckBox(CheckBox.tr("Both directions"))
        self._full_length_checkbox.setChecked(False)
        self._full_length_checkbox.toggled.connect(self._full_length_checkbox_toggled_handler)

        self._center_checkbox = CheckBox(CheckBox.tr("Center"))
        self._center_checkbox.setChecked(False)
        self._center_checkbox.toggled.connect(self._center_checkbox_toggled_handler)

        layout.addWidget(self._visibility_checkbox, 0, 0)
        layout.addWidget(self._labels_visibility_checkbox, 0, 1)
        layout.addWidget(self._full_length_checkbox, 1, 0)
        layout.addWidget(self._center_checkbox, 1, 1)

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
            factor=100,
            decimals=1,
        )
        self.length_slider.valueChanged.connect(self.length_slider_value_changed_handler)
        self.length_double_spinbox.valueChanged.connect(self.length_double_spinbox_value_changed_handler)

        self.thickness_slider, self.thickness_double_spinbox = add_slider(
            layout=layout,
            row=1,
            text=Label.tr("Thickness:"),
            min_value=0.03,
            max_value=1.0,
            single_step=0.01,
            factor=100,
            decimals=2,
        )
        self.thickness_slider.valueChanged.connect(self.thickness_slider_value_changed_handler)
        self.thickness_double_spinbox.valueChanged.connect(self.thickness_double_spinbox_value_changed_handler)

        self.label_size_slider, self.label_size_double_spinbox = add_slider(
            layout=layout,
            row=2,
            text=Label.tr("Font size:"),
            min_value=16,
            max_value=500,
            single_step=1,
        )
        self.label_size_slider.valueChanged.connect(self.label_size_slider_value_changed_handler)
        self.label_size_double_spinbox.valueChanged.connect(self.label_size_double_spinbox_value_changed_handler)

        adjust_length_button = PushButton(PushButton.tr("Adjust length"))
        adjust_length_button.clicked.connect(self._adjust_labels_length_button_clicked_handler)

        layout.addWidget(adjust_length_button, 3, 0, 1, 3)

        return layout

    def _add_axes(self) -> QGridLayout:
        layout = QGridLayout()

        self._x_axis_color_button, self._x_label_color_button, self._x_line_edit = self._add_axis(
            layout, 0, Label.tr("Axis X:"), "x"
        )
        self._y_axis_color_button, self._y_label_color_button, self._y_line_edit = self._add_axis(
            layout, 1, Label.tr("Axis Y:"), "y"
        )
        self._z_axis_color_button, self._z_label_color_button, self._z_line_edit = self._add_axis(
            layout, 2, Label.tr("Axis Z:"), "z"
        )

        return layout

    def _add_axis(
        self, layout: QGridLayout, row: int, label_text: TrString, axis: str
    ) -> tuple[ColorButton, ColorButton, QLineEdit]:
        label = Label(label_text)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        axis_color_button = ColorButton()
        axis_color_button.color_changed.connect(lambda color: self._axis_color_changed_handler(axis, color))

        label_color_button = ColorButton()
        label_color_button.color_changed.connect(lambda color: self._axis_label_color_changed_handler(axis, color))

        line_edit = QLineEdit()
        line_edit.textChanged.connect(lambda text: self._axis_text_changed_handler(axis, text))

        layout.addWidget(label, row, 0)
        layout.addWidget(axis_color_button, row, 1)
        layout.addWidget(label_color_button, row, 2)
        layout.addWidget(line_edit, row, 3)

        return axis_color_button, label_color_button, line_edit

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

    def _axis_label_color_changed_handler(self, axis: str, color: QColor):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axis_label_color(axis, qcolor_to_color4f(color))

    def _axis_color_changed_handler(self, axis: str, color: QColor):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axis_color(axis, qcolor_to_color4f(color))

    def _axis_text_changed_handler(self, axis: str, text: str):
        for viewer in self._settings.viewers:
            viewer.visualizer.set_coordinate_axis_text(axis, text)

    def _adjust_labels_length_button_clicked_handler(self):
        for viewer in self._settings.viewers:
            viewer.visualizer.adjust_coordinate_axes_length()

    def update_values(self, viewer: "MolecularStructureViewer"):
        coordinate_axes = viewer.visualizer.coordinate_axes

        self._visibility_checkbox.setChecked(coordinate_axes.visible)
        self._labels_visibility_checkbox.setChecked(coordinate_axes.labels_visible)
        self._full_length_checkbox.setChecked(coordinate_axes.full_length)
        self._center_checkbox.setChecked(not coordinate_axes.at_000)

        self.length_slider.setValue(int(coordinate_axes.length * 100))
        self.length_double_spinbox.setValue(coordinate_axes.length)

        self.thickness_slider.setValue(int(coordinate_axes.thickness * 100))
        self.thickness_double_spinbox.setValue(coordinate_axes.thickness)

        self.label_size_slider.setValue(coordinate_axes.labels_size)
        self.label_size_double_spinbox.setValue(coordinate_axes.labels_size)

        self._x_axis_color_button.set_color(color4f_to_qcolor(coordinate_axes.x.axis_color))
        self._y_axis_color_button.set_color(color4f_to_qcolor(coordinate_axes.y.axis_color))
        self._z_axis_color_button.set_color(color4f_to_qcolor(coordinate_axes.z.axis_color))

        self._x_label_color_button.set_color(color4f_to_qcolor(coordinate_axes.x.label_color))
        self._y_label_color_button.set_color(color4f_to_qcolor(coordinate_axes.y.label_color))
        self._z_label_color_button.set_color(color4f_to_qcolor(coordinate_axes.z.label_color))

        self._x_line_edit.setText(coordinate_axes.x.label_text)
        self._y_line_edit.setText(coordinate_axes.y.label_text)
        self._z_line_edit.setText(coordinate_axes.z.label_text)
