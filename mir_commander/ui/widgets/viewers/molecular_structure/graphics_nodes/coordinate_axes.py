from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType, TextNode
from mir_commander.ui.utils.opengl.utils import Color4f

from .cone import Cone
from .cylinder import Cylinder
from .sphere import Sphere


class AxisLabel(TextNode):
    def __init__(self, color: Color4f, text: str, size: int, *args, **kwargs):
        kwargs["visible"] = True
        kwargs["align"] = "center"
        super().__init__(*args, **kwargs)

        s = size / 100.0

        self.set_scale(QVector3D(s, s, s))
        self.set_color(color)
        self.set_text(text)

    def set_size(self, value: int):
        s = value / 100.0
        self.set_scale(QVector3D(s, s, s))


class Axis(Node):
    def __init__(self, direction: QVector3D, color: Color4f, text: str, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._direction = direction
        self._length = 0.5
        self._thickness = 0.03
        self._cone_radius_factor = 2.0
        self._cone_length_factor = 6.0
        self._full_length = False

        self._cylinder = Cylinder(direction, parent=self, node_type=NodeType.OPAQUE)
        self._cylinder.set_shader("default")
        self._cylinder.set_color(color)

        self._cone = Cone(direction, parent=self, node_type=NodeType.OPAQUE)
        self._cone.set_shader("default")
        self._cone.set_color(color)

        self._axis_label = AxisLabel(color, text, 16, parent=self)

        self._sphere = Sphere(self._thickness, parent=self, node_type=NodeType.OPAQUE, visible=False)
        self._sphere.set_shader("default")
        self._sphere.set_color(color)

        self._update()

    @property
    def thickness(self) -> float:
        return self._thickness

    @property
    def length(self) -> float:
        return self._length

    def set_color(self, color: Color4f):
        self._cylinder.set_color(color)
        self._cone.set_color(color)
        self._sphere.set_color(color)

    def set_thickness(self, value: float):
        self._thickness = value
        self._update()

    def set_length(self, length: float):
        self._length = length
        self._update()

    def _update(self):
        self._cylinder.set_radius(self._thickness)
        if self._full_length:
            self._cylinder.set_length(self._length * 2)
            self._cylinder.set_translation(-self._direction * self._length)
            self._sphere.set_visible(True)
        else:
            self._cylinder.set_length(self._length)
            self._cylinder.set_translation(QVector3D(0.0, 0.0, 0.0))
            self._sphere.set_visible(False)

        self._cone.set_size(self._thickness * self._cone_radius_factor, self._thickness * self._cone_length_factor)
        self._cone.set_translation(self._direction * self._length)

        self._sphere.set_radius(self._thickness)
        self._sphere.set_translation(-self._direction * self._length)
        self._axis_label.set_translation(
            self._direction * self._length + self._direction * (self._thickness * self._cone_length_factor * 2)
        )

    def set_text(self, text: str):
        self._axis_label.set_text(text)

    def set_label_color(self, color: Color4f):
        self._axis_label.set_color(color)

    def set_label_visible(self, value: bool):
        self._axis_label.set_visible(value)

    def set_label_size(self, value: int):
        self._axis_label.set_size(value)

    def set_full_length(self, value: bool):
        self._full_length = value
        self._update()


class CoordinateAxes(Node):
    def __init__(self, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = False
        super().__init__(*args, **kwargs)

        self._x = Axis(QVector3D(1.0, 0.0, 0.0), (1.0, 0.4, 0.4, 1.0), "x", parent=self)
        self._y = Axis(QVector3D(0.0, 1.0, 0.0), (0.4, 1.0, 0.4, 1.0), "y", parent=self)
        self._z = Axis(QVector3D(0.0, 0.0, 1.0), (0.4, 0.4, 1.0, 1.0), "z", parent=self)
        self._sphere = Sphere(self._x.thickness, parent=self, node_type=NodeType.OPAQUE)
        self._sphere.set_shader("default")
        self._sphere.set_color((0.0, 0.0, 0.0, 1.0))

    @property
    def x(self) -> Axis:
        return self._x

    @property
    def y(self) -> Axis:
        return self._y

    @property
    def z(self) -> Axis:
        return self._z

    def set_thickness(self, value: float):
        self._x.set_thickness(value)
        self._y.set_thickness(value)
        self._z.set_thickness(value)
        self._sphere.set_radius(value)

    def set_length(self, value: float):
        self._x.set_length(value)
        self._y.set_length(value)
        self._z.set_length(value)

    def set_labels_visible(self, value: bool):
        self._x.set_label_visible(value)
        self._y.set_label_visible(value)
        self._z.set_label_visible(value)

    def set_labels_size(self, value: int):
        self._x.set_label_size(value)
        self._y.set_label_size(value)
        self._z.set_label_size(value)

    def set_full_length(self, value: bool):
        self._x.set_full_length(value)
        self._y.set_full_length(value)
        self._z.set_full_length(value)
