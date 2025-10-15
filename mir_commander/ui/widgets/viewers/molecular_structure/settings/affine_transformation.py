import contextlib
from typing import TYPE_CHECKING

from PySide6.QtCore import QSignalBlocker
from PySide6.QtWidgets import QDoubleSpinBox, QGridLayout, QSlider, QVBoxLayout

from mir_commander.ui.utils.widget import GroupBox, Label, PushButton, TrString

from .utils import add_slider

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer
    from .settings import Settings


class AffineTransformation(GroupBox):
    def __init__(self, parent: "Settings"):
        super().__init__(text=self.tr("Affine Transformation"), parent=parent)

        self._settings = parent

        self._axis_prev_value: dict[str, float] = {}
        self._scale_prev_value: float = 0.0
        self._axis_order = ("pitch", "yaw", "roll")
        self._rotation_slider: dict[str, QSlider] = {}
        self._rotation_double_spinbox: dict[str, QDoubleSpinBox] = {}

        reset_button = PushButton(PushButton.tr("Reset"))
        reset_button.clicked.connect(self._reset_button_clicked_handler)

        layout = QVBoxLayout(self)
        layout.addLayout(self._add_translations())
        layout.addWidget(reset_button)
        self.setLayout(layout)

    def _add_translations(self) -> QGridLayout:
        layout = QGridLayout()

        self._add_axis_rotation(
            layout,
            0,
            Label.tr("Rotation X:"),
            "pitch",
            Label.tr("Rotation angle around the X-axis in window coordinates"),
        )
        self._add_axis_rotation(
            layout,
            1,
            Label.tr("Rotation Y:"),
            "yaw",
            Label.tr("Rotation angle around the Y-axis in window coordinates"),
        )
        self._add_axis_rotation(
            layout,
            2,
            Label.tr("Rotation Z:"),
            "roll",
            Label.tr("Rotation angle around the Z-axis in window coordinates"),
        )

        self._scale_slider, self._scale_double_spinbox = add_slider(
            layout=layout,
            row=3,
            text=Label.tr("Scale:"),
            min_value=0.01,
            max_value=10.0,
            single_step=0.01,
            decimals=2,
            factor=100,
        )
        self._scale_slider.valueChanged.connect(self._scale_slider_value_changed_handler)
        self._scale_double_spinbox.valueChanged.connect(self._scale_double_spinbox_value_changed_handler)

        return layout

    def _add_axis_rotation(
        self, layout: QGridLayout, row: int, label_text: TrString, axis: str, label_tooltip: TrString | None = None
    ):
        self._axis_prev_value[axis] = 0.0
        self._rotation_slider[axis], self._rotation_double_spinbox[axis] = add_slider(
            layout=layout,
            row=row,
            text=label_text,
            min_value=-180,
            max_value=180,
            single_step=0.1,
            decimals=1,
            factor=10,
            label_tooltip=label_tooltip,
        )
        self._rotation_slider[axis].valueChanged.connect(lambda i: self._rotation_slider_value_changed_handler(axis, i))
        self._rotation_double_spinbox[axis].valueChanged.connect(
            lambda value: self._rotation_double_spinbox_value_changed_handler(axis, value)
        )

    def update_values(self, viewer: "MolecularStructureViewer"):
        values = {axis: value for axis, value in zip(self._axis_order, viewer.visualizer.scene_rotation)}

        with contextlib.ExitStack() as stack:
            for axis in self._axis_order:
                stack.enter_context(QSignalBlocker(self._rotation_slider[axis]))
                stack.enter_context(QSignalBlocker(self._rotation_double_spinbox[axis]))
            stack.enter_context(QSignalBlocker(self._scale_slider))
            stack.enter_context(QSignalBlocker(self._scale_double_spinbox))

            for axis, value in values.items():
                self._axis_prev_value[axis] = value
                self._rotation_slider[axis].setValue(int(value * 10))
                self._rotation_double_spinbox[axis].setValue(value)

            self._scale_prev_value = scale = viewer.visualizer.get_scene_scale()
            self._scale_slider.setValue(int(scale * 100))
            self._scale_double_spinbox.setValue(scale)

    def _rotation_slider_value_changed_handler(self, axis: str, i: int):
        self._rotation_double_spinbox[axis].setValue(i / 10)

    def _rotation_double_spinbox_value_changed_handler(self, axis: str, value: float):
        self._rotation_slider[axis].setValue(int(value * 10))

        data = {key: value.value() - self._axis_prev_value[key] for key, value in self._rotation_double_spinbox.items()}
        for viewer in self._settings.viewers:
            viewer.visualizer.rotate_scene(**data)
        self._axis_prev_value[axis] = value

    def _scale_slider_value_changed_handler(self, i: int):
        self._scale_double_spinbox.setValue(i / 100)

    def _scale_double_spinbox_value_changed_handler(self, value: float):
        self._scale_slider.setValue(int(value * 100))
        v = value / self._scale_prev_value

        for viewer in self._settings.viewers:
            viewer.visualizer.scale_scene(v)
        self._scale_prev_value = value

    def _reset_button_clicked_handler(self):
        with contextlib.ExitStack() as stack:
            for axis in self._axis_order:
                stack.enter_context(QSignalBlocker(self._rotation_slider[axis]))
                stack.enter_context(QSignalBlocker(self._rotation_double_spinbox[axis]))
            stack.enter_context(QSignalBlocker(self._scale_slider))
            stack.enter_context(QSignalBlocker(self._scale_double_spinbox))
            for axis in self._axis_order:
                self._axis_prev_value[axis] = 0.0
                self._rotation_slider[axis].setValue(0)
                self._rotation_double_spinbox[axis].setValue(0)
            self._scale_prev_value = 1.0
            self._scale_slider.setValue(100)
            self._scale_double_spinbox.setValue(1.0)

        for viewer in self._settings.viewers:
            viewer.visualizer.set_scene_rotation(0, 0, 0)
            viewer.visualizer.set_scene_scale(1.0)
