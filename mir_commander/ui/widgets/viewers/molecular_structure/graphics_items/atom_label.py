from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager import SceneNode
from mir_commander.ui.utils.opengl.utils import Color4f


class Char(SceneNode):
    def __init__(self, char: str, position: QVector3D, color: Color4f):
        super().__init__(transparent=True)
        self.translate(position)
        self.set_color(color)
        self.set_model(f"arial_{char}")
        self.set_shader("text")
        self.set_texture("font_atlas_arial")


class AtomLabel(SceneNode):
    def __init__(
        self,
        symbol: str,
        index: int,
        position: QVector3D,
        color: Color4f = (0.0, 0.0, 0.0, 1.0),
    ):
        super().__init__(is_container=True)
        self.set_scale(QVector3D(0.4, 0.4, 0.4))

        for i, char in enumerate(f"{symbol}{index}"):
            self.add_node(Char(char, QVector3D(i, 0, 0), color))
