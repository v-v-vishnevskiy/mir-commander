from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager import SceneNode
from mir_commander.ui.utils.opengl.utils import Color4f


class AtomLabel(SceneNode):
    def __init__(
        self,
        symbol: str,
        index: int,
        position: QVector3D,
        color: Color4f = (0.0, 0.0, 0.0, 1.0),
    ):
        super().__init__(transparent=True, picking_visible=False)
        self.set_color(color)
        self.set_scale(QVector3D(0.4, 0.4, 0.4))
        self.set_model(f"arial_{symbol[0]}")
        self.set_shader("text")
        self.set_texture("font_atlas_arial")
