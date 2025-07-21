from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager import SceneTextNode
from mir_commander.ui.utils.opengl.utils import Color4f


class AtomLabel(SceneTextNode):
    def __init__(self, color: Color4f = (0.0, 0.0, 0.0, 1.0)):
        super().__init__(font_atlas_name="arial", align="center")
        self.set_scale(QVector3D(0.4, 0.4, 0.4))
        self.set_color(color)
        self.set_shader("text")
        self.set_texture("font_atlas_arial")
