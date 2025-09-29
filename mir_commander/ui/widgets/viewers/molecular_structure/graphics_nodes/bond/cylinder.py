from typing import TYPE_CHECKING

from PySide6.QtGui import QQuaternion, QVector3D

from mir_commander.ui.utils.opengl.scene import NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from ...consts import VAO_CYLINDER_RESOURCE_NAME
from ..base import BaseGraphicsNode

if TYPE_CHECKING:
    from .bond import Bond


class Cylinder(BaseGraphicsNode):
    def __init__(
        self,
        parent: "Bond",
        position: QVector3D,
        direction: QVector3D,
        radius: float,
        length: float,
        color: Color4f,
    ):
        super().__init__(parent=parent, node_type=NodeType.OPAQUE, visible=True, picking_visible=False)
        self._length = length
        self.set_shader("default")
        self.set_model(VAO_CYLINDER_RESOURCE_NAME)
        self.set_color(color)
        self.set_translation(position)
        self.set_rotation(QQuaternion.rotationTo(QVector3D(0.0, 0.0, -1.0), direction))
        self.set_scale(QVector3D(radius, radius, length))

    def set_radius(self, radius: float):
        self.set_scale(QVector3D(radius, radius, self._length))
