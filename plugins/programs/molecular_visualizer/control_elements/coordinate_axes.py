from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLineEdit

from mir_commander.core.graphics.utils import color4f_to_qcolor, qcolor_to_color4f
from mir_commander.ui.sdk.widget import CheckBox, ColorButton, GridLayout, Label, PushButton, TrString, VBoxLayout

from ...program import ControlBlock
from .utils import add_slider

if TYPE_CHECKING:
    from ..control_panel import ControlPanel
    from ..program import Program


class CoordinateAxes(ControlBlock):
    def __init__(self, control_panel: "ControlPanel"):
        super().__init__()

        self._control_panel = control_panel

        self._layouts: list[GridLayout] = [self._add_checkboxes(), self._add_sliders(), self._add_axes()]

        layout = VBoxLayout()
        for item in self._layouts:
            layout.addLayout(item)
        self.setLayout(layout)

    def _add_checkboxes(self) -> GridLayout:
        layout = GridLayout()

        self._visibility_checkbox = CheckBox(CheckBox.tr("Show"))
        self._visibility_checkbox.setChecked(False)
        self._visibility_checkbox.toggled.connect(self._visibility_checkbox_toggled_handler)

        self._labels_visibility_checkbox = CheckBox(CheckBox.tr("Labels"))
        self._labels_visibility_checkbox.setChecked(True)
        self._labels_visibility_checkbox.toggled.connect(self._labels_visibility_checkbox_toggled_handler)

        self._both_directions_checkbox = CheckBox(CheckBox.tr("Both directions"))
        self._both_directions_checkbox.setChecked(False)
        self._both_directions_checkbox.toggled.connect(self._both_directions_checkbox_toggled_handler)

        self._center_checkbox = CheckBox(CheckBox.tr("Center"))
        self._center_checkbox.setChecked(False)
        self._center_checkbox.toggled.connect(self._center_checkbox_toggled_handler)

        layout.addWidget(self._visibility_checkbox, 0, 0)
        layout.addWidget(self._labels_visibility_checkbox, 0, 1)
        layout.addWidget(self._both_directions_checkbox, 1, 0)
        layout.addWidget(self._center_checkbox, 1, 1)

        return layout

    def _add_sliders(self) -> GridLayout:
        layout = GridLayout()

        self._length_slider, self._length_double_spinbox = add_slider(
            layout=layout,
            row=0,
            text=Label.tr("Length:"),
            min_value=0.5,
            max_value=100.0,
            single_step=0.1,
            factor=100,
            decimals=1,
        )
        self._length_slider.valueChanged.connect(self._length_slider_value_changed_handler)
        self._length_double_spinbox.valueChanged.connect(self._length_double_spinbox_value_changed_handler)

        self._thickness_slider, self._thickness_double_spinbox = add_slider(
            layout=layout,
            row=1,
            text=Label.tr("Thickness:"),
            min_value=0.03,
            max_value=1.0,
            single_step=0.01,
            factor=100,
            decimals=2,
        )
        self._thickness_slider.valueChanged.connect(self._thickness_slider_value_changed_handler)
        self._thickness_double_spinbox.valueChanged.connect(self._thickness_double_spinbox_value_changed_handler)

        self._font_size_slider, self._font_size_double_spinbox = add_slider(
            layout=layout,
            row=2,
            text=Label.tr("Font size:"),
            min_value=16,
            max_value=500,
            single_step=1,
        )
        self._font_size_slider.valueChanged.connect(self._font_size_slider_value_changed_handler)
        self._font_size_double_spinbox.valueChanged.connect(self._font_size_double_spinbox_value_changed_handler)

        adjust_length_button = PushButton(PushButton.tr("Adjust length"))
        adjust_length_button.clicked.connect(self._adjust_labels_length_button_clicked_handler)

        layout.addWidget(adjust_length_button, 3, 0, 1, 3)

        return layout

    def _add_axes(self) -> GridLayout:
        layout = GridLayout()

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
        self, layout: GridLayout, row: int, label_text: TrString, axis: str
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
        self._enable_controls(value)
        self._control_panel.program_action_signal.emit("coordinate_axes.set_visible", {"value": value})

    def _labels_visibility_checkbox_toggled_handler(self, value: bool):
        self._control_panel.program_action_signal.emit("coordinate_axes.set_labels_visible", {"value": value})

    def _both_directions_checkbox_toggled_handler(self, value: bool):
        self._control_panel.program_action_signal.emit("coordinate_axes.set_both_directions", {"value": value})

    def _center_checkbox_toggled_handler(self, value: bool):
        self._control_panel.program_action_signal.emit("coordinate_axes.set_to_center", {"value": value})

    def _length_slider_value_changed_handler(self, i: int):
        self._length_double_spinbox.setValue(i / 100)
        self._control_panel.program_action_signal.emit("coordinate_axes.set_length", {"value": i / 100})

    def _length_double_spinbox_value_changed_handler(self, value: float):
        self._length_slider.setValue(int(value * 100))

    def _thickness_slider_value_changed_handler(self, i: int):
        self._thickness_double_spinbox.setValue(i / 100)
        self._control_panel.program_action_signal.emit("coordinate_axes.set_thickness", {"value": i / 100})

    def _thickness_double_spinbox_value_changed_handler(self, value: float):
        self._thickness_slider.setValue(int(value * 100))

    def _font_size_slider_value_changed_handler(self, i: int):
        self._font_size_double_spinbox.setValue(i)
        self._control_panel.program_action_signal.emit("coordinate_axes.set_font_size", {"value": i})

    def _font_size_double_spinbox_value_changed_handler(self, value: int):
        self._font_size_slider.setValue(value)

    def _axis_label_color_changed_handler(self, axis: str, color: QColor):
        self._control_panel.program_action_signal.emit(
            "coordinate_axes.set_label_color", {"axis": axis, "color": qcolor_to_color4f(color)}
        )

    def _axis_color_changed_handler(self, axis: str, color: QColor):
        self._control_panel.program_action_signal.emit(
            "coordinate_axes.set_color", {"axis": axis, "color": qcolor_to_color4f(color)}
        )

    def _axis_text_changed_handler(self, axis: str, text: str):
        self._control_panel.program_action_signal.emit("coordinate_axes.set_text", {"axis": axis, "text": text})

    def _adjust_labels_length_button_clicked_handler(self):
        self._control_panel.program_action_signal.emit("coordinate_axes.adjust_length", {})

    def _enable_controls(self, enabled: bool):
        for layout in self._layouts:
            for i in range(layout.rowCount()):
                for j in range(layout.columnCount()):
                    item = layout.itemAtPosition(i, j)
                    if item is not None:
                        item.widget().setEnabled(enabled)

        self._visibility_checkbox.setEnabled(True)

    def update_values(self, program: "Program"):
        coordinate_axes = program.visualizer.coordinate_axes

        self._visibility_checkbox.setChecked(coordinate_axes.visible)
        self._labels_visibility_checkbox.setChecked(coordinate_axes.labels_visible)
        self._both_directions_checkbox.setChecked(coordinate_axes.both_directions)
        self._center_checkbox.setChecked(not coordinate_axes.at_000)

        self._length_slider.setValue(int(coordinate_axes.length * 100))
        self._length_double_spinbox.setValue(coordinate_axes.length)

        self._thickness_slider.setValue(int(coordinate_axes.thickness * 100))
        self._thickness_double_spinbox.setValue(coordinate_axes.thickness)

        self._font_size_slider.setValue(coordinate_axes.labels_size)
        self._font_size_double_spinbox.setValue(coordinate_axes.labels_size)

        self._x_axis_color_button.set_color(color4f_to_qcolor(coordinate_axes.x.axis_color))
        self._y_axis_color_button.set_color(color4f_to_qcolor(coordinate_axes.y.axis_color))
        self._z_axis_color_button.set_color(color4f_to_qcolor(coordinate_axes.z.axis_color))

        self._x_label_color_button.set_color(color4f_to_qcolor(coordinate_axes.x.label_color))
        self._y_label_color_button.set_color(color4f_to_qcolor(coordinate_axes.y.label_color))
        self._z_label_color_button.set_color(color4f_to_qcolor(coordinate_axes.z.label_color))

        self._x_line_edit.setText(coordinate_axes.x.label_text)
        self._y_line_edit.setText(coordinate_axes.y.label_text)
        self._z_line_edit.setText(coordinate_axes.z.label_text)

        self._enable_controls(coordinate_axes.visible)
