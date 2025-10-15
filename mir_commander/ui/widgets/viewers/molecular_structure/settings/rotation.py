import contextlib
from typing import TYPE_CHECKING

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout

from mir_commander.ui.utils.widget import GroupBox, Label, PushButton, TrString

from .utils import add_slider

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer
    from .settings import Settings


class Rotation(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(text=self.tr("Rotation"), parent=parent)

        self._settings = parent

        self._axis_order = ("pitch", "yaw", "roll")
        self._prev_value: dict[str, float] = {}
        self._rotation_slider: dict[str, QSlider] = {}
        self._rotation_double_spinbox: dict[str, QDoubleSpinBox] = {}

        reset_button = PushButton(PushButton.tr("Reset"))
        reset_button.clicked.connect(self._reset_button_clicked_handler)

        layout = QVBoxLayout(self)
        layout.addLayout(self._add_rotating())
        layout.addWidget(reset_button)
        self.setLayout(layout)

    def _add_rotating(self) -> QGridLayout:
        layout = QGridLayout()

        self._add_axis_rotation(layout, 0, Label.tr("Axis X:"), "pitch")
        self._add_axis_rotation(layout, 1, Label.tr("Axis Y:"), "yaw")
        self._add_axis_rotation(layout, 2, Label.tr("Axis Z:"), "roll")

        return layout

    def _add_axis_rotation(self, layout: QGridLayout, row: int, label_text: TrString, axis: str):
        self._prev_value[axis] = 0.0
        self._rotation_slider[axis], self._rotation_double_spinbox[axis] = add_slider(
            layout=layout,
            row=row,
            text=label_text,
            min_value=-180,
            max_value=180,
            single_step=0.1,
            decimals=1,
            factor=10,
        )
        self._rotation_slider[axis].valueChanged.connect(lambda i: self._rotation_slider_value_changed_handler(axis, i))
        self._rotation_double_spinbox[axis].valueChanged.connect(
            lambda value: self._rotation_double_spinbox_value_changed_handler(axis, value)
        )

    def update_values(self, viewer: "MolecularStructureViewer"):
        values = {axis: value for axis, value in zip(self._axis_order, viewer.visualizer.rotation)}

        with contextlib.ExitStack() as stack:
            for axis in self._axis_order:
                stack.enter_context(QSignalBlocker(self._rotation_slider[axis]))
                stack.enter_context(QSignalBlocker(self._rotation_double_spinbox[axis]))

            for axis, value in values.items():
                self._prev_value[axis] = value
                self._rotation_slider[axis].setValue(int(value * 10))
                self._rotation_double_spinbox[axis].setValue(value)

    def _rotation_slider_value_changed_handler(self, axis: str, i: int):
        self._rotation_double_spinbox[axis].setValue(i / 10)

    def _rotation_double_spinbox_value_changed_handler(self, axis: str, value: float):
        self._rotation_slider[axis].setValue(int(value * 10))

        data = {key: value.value() - self._prev_value[key] for key, value in self._rotation_double_spinbox.items()}
        for viewer in self._settings.viewers:
            viewer.visualizer.rotate_scene(**data)
        self._prev_value[axis] = value

    def _reset_button_clicked_handler(self):
        with contextlib.ExitStack() as stack:
            for axis in self._axis_order:
                stack.enter_context(QSignalBlocker(self._rotation_slider[axis]))
                stack.enter_context(QSignalBlocker(self._rotation_double_spinbox[axis]))
            for axis in self._axis_order:
                self._prev_value[axis] = 0.0
                self._rotation_slider[axis].setValue(0)
                self._rotation_double_spinbox[axis].setValue(0)

        for viewer in self._settings.viewers:
            viewer.visualizer.set_rotation_scene(0, 0, 0)
