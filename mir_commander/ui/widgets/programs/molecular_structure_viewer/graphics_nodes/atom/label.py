from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, TextNode
from mir_commander.ui.utils.opengl.utils import color_to_color4f

from ...config import AtomLabelConfig


class Label(TextNode):
    def __init__(self, parent: Node, config: AtomLabelConfig):
        super().__init__(parent=parent, visible=config.visible, align="center")
        s = config.size / 100.0
        self.set_scale(QVector3D(s, s, s))
        self.set_shader("atom_label")
        self.set_color(color_to_color4f(config.color))

    def set_config(self, config: AtomLabelConfig):
        self.set_color(color_to_color4f(config.color))
        s = config.size / 100.0
        self.set_scale(QVector3D(s, s, s))
        self.set_font_atlas_name(config.font)

    def set_size(self, size: int):
        s = size / 100.0
        self.set_scale(QVector3D(s, s, s))
