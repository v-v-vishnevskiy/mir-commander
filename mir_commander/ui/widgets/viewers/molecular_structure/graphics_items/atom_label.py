from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import BaseNode, TextNode
from mir_commander.ui.utils.opengl.utils import Color4f


class AtomLabel(TextNode):
    def __init__(self, parent: BaseNode, color: Color4f = (0.0, 0.0, 0.0, 1.0)):
        super().__init__(
            parent=parent, 
            visible=False, 
            picking_visible=False, 
            font_atlas_name="default",
            align="center"
        )
        self.set_scale(QVector3D(0.35, 0.35, 0.35))
        self.set_shader("text")
        self.set_color(color)
