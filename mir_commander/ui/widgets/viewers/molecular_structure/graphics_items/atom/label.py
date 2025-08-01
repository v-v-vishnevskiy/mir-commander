from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import BaseNode, TextNode
from mir_commander.ui.utils.opengl.utils import color_to_color4f

from ...config import AtomLabelConfig


class Label(TextNode):
    def __init__(self, parent: BaseNode, config: AtomLabelConfig):
        super().__init__(parent=parent, visible=config.visible, picking_visible=False, align="center")
        self._config = config
        self.set_scale(QVector3D(config.size, config.size, config.size))
        self.set_shader("atom_label")
        self.set_color(color_to_color4f(config.color))

    def set_config(self, config: AtomLabelConfig):
        self.set_color(color_to_color4f(config.color))
        self.set_scale(QVector3D(config.size, config.size, config.size))
        self.set_font_atlas_name(config.font)

    def set_size(self, size: float):
        self.set_scale(QVector3D(size, size, size))
