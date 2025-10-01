from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from ...consts import VAO_SPHERE_RESOURCE_NAME
from .sphere import Sphere


class Surface(Node):
    def __init__(self, value: float, points: list[QVector3D], color: Color4f, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._value = value
        self._points = points
        self._color = color

        self._build()

    @property
    def value(self) -> float:
        return self._value

    def _build(self):
        self.clear()

        for point in self._points:
            s = Sphere(parent=self)
            s.translate(point)
            s.set_scale(QVector3D(0.2, 0.2, 0.2))
            s.set_color(self._color)
            s.set_model(VAO_SPHERE_RESOURCE_NAME)
            s.set_shader("transparent")
