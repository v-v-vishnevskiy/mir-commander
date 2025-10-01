from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import NodeType

from ...consts import VAO_SPHERE_RESOURCE_NAME
from ..base import BaseGraphicsNode


class Sphere(BaseGraphicsNode):
    def __init__(self, position: QVector3D, *args, **kwargs):
        kwargs["node_type"] = NodeType.TRANSPARENT
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self.translate(position)
        self.set_scale(QVector3D(0.2, 0.2, 0.2))
        self.set_color((1.0, 1.0, 0.0, 0.5))
        self.set_model(VAO_SPHERE_RESOURCE_NAME)
        self.set_shader("transparent")
