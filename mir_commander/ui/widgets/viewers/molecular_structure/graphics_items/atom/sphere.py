from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import BaseNode, OpaqueNode
from mir_commander.ui.utils.opengl.utils import Color4f


class Sphere(OpaqueNode):
    def __init__(self, parent: BaseNode, model_name: str, radius: float, color: Color4f):
        super().__init__(parent=parent, visible=True, picking_visible=True)
        self.set_scale(QVector3D(radius, radius, radius))
        self.set_color(color)
        self.set_model(model_name)
        self.set_shader("default")

        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(QVector3D(radius, radius, radius))

    def highlight(self, value: bool) -> float:
        if value:
            radius = self._radius * 1.15
        else:
            radius = self._radius
        self.set_scale(QVector3D(radius, radius, radius))
        return radius
