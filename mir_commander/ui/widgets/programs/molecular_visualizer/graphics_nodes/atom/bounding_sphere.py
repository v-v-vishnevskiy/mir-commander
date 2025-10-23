from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, color_to_color4f

from ...config import SelectedAtom
from ...consts import VAO_SPHERE_RESOURCE_NAME


class BoundingSphere(Node):
    def __init__(self, config: SelectedAtom, *args, **kwargs):
        super().__init__(*args, **kwargs | dict(node_type=NodeType.TRANSPARENT, visible=False, picking_visible=False))
        self._config = config

        self.set_scale(QVector3D(config.scale_factor, config.scale_factor, config.scale_factor))
        self.set_shader("transparent_flat")
        self.set_model(VAO_SPHERE_RESOURCE_NAME)
        self.set_color(self._compute_color(config))

    def set_config(self, config: SelectedAtom):
        self._config = config
        self.set_color(self._compute_color(config))
        self.set_scale(QVector3D(config.scale_factor, config.scale_factor, config.scale_factor))

    def _compute_color(self, config: SelectedAtom) -> Color4f:
        r, g, b, _ = color_to_color4f(config.color)
        return r, g, b, config.opacity
