from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from .cone import Cone
from .cylinder import Cylinder


class Axis(Node):
    def __init__(self, direction: QVector3D, length: float, radius: float, color: Color4f, text: str, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._text = text

        self._cylinder = Cylinder(direction, radius, length, parent=self, node_type=NodeType.OPAQUE)
        self._cylinder.set_shader("default")
        self._cylinder.set_color(color)

        self._cone = Cone(direction, radius * 3, radius * 6, parent=self, node_type=NodeType.OPAQUE)
        self._cone.set_shader("default")
        self._cone.set_color(color)
        self._cone.set_translation(-direction * length)

    def set_color(self, color: Color4f):
        self._cylinder.set_color(color)
        self._cone.set_color(color)

    def set_radius(self, radius: float):
        self._cylinder.set_radius(radius)
        self._cone.set_radius(radius * 3)

    def set_length(self, length: float):
        self._cylinder.set_length(length)
        self._cone.set_length(length * 6)

    def set_text(self, text: str):
        self._text = text
