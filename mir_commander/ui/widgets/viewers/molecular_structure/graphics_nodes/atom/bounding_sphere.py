from pydantic_extra_types.color import Color
from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, color_to_color4f

from ...config import SelectedAtom
from ...consts import VAO_SPHERE_RESOURCE_NAME


class BoundingSphere(Node):
    def __init__(
        self,
        parent: Node,
        atom_color: Color4f,
        config: SelectedAtom,
    ):
        super().__init__(parent=parent, node_type=NodeType.TRANSPARENT, visible=False, picking_visible=False)
        self._atom_color = atom_color
        self._config = config

        self.set_scale(QVector3D(config.scale_factor, config.scale_factor, config.scale_factor))
        self.set_shader("transparent")
        self.set_model(VAO_SPHERE_RESOURCE_NAME)
        self.set_color(self._compute_color(config))

    def set_config(self, config: SelectedAtom):
        self._config = config
        self.set_color(self._compute_color(config))
        self.set_scale(QVector3D(config.scale_factor, config.scale_factor, config.scale_factor))

    def _compute_color(self, config: SelectedAtom) -> Color4f:
        if type(config.color) is Color:
            r, g, b, _ = color_to_color4f(config.color)
            return r, g, b, config.opacity
        return self._atom_color[0], self._atom_color[1], self._atom_color[2], config.opacity
