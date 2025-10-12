from enum import Enum

from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from .axis import Axis
from .sphere import Sphere


class AxisType(Enum):
    X = 0
    Y = 1
    Z = 2


class CoordinateAxes(Node):
    def __init__(self, color: Color4f, radius: float, length: float, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._axes = {
            AxisType.X: Axis(QVector3D(1.0, 0.0, 0.0), length, radius, color, "x", parent=self),
            AxisType.Y: Axis(QVector3D(0.0, 1.0, 0.0), length, radius, color, "y", parent=self),
            AxisType.Z: Axis(QVector3D(0.0, 0.0, 1.0), length, radius, color, "z", parent=self),
        }
        self._sphere = Sphere(radius, parent=self, node_type=NodeType.OPAQUE)
        self._sphere.set_shader("default")
        self._sphere.set_color(color)

    def set_axis_color(self, axis: AxisType, color: Color4f):
        self._axes[axis].set_color(color)

    def set_axis_text(self, axis: AxisType, text: str):
        self._axes[axis].set_text(text)

    def set_radius(self, radius: float):
        for c in self._axes.values():
            c.set_radius(radius)
        self._sphere.set_radius(radius)

    def set_length(self, length: float):
        for c in self._axes.values():
            c.set_length(length)
