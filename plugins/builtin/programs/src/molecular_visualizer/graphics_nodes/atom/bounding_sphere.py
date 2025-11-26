from mir_commander.core.algebra import Vector3D
from mir_commander.core.graphics.scene.node import Node, NodeType
from mir_commander.core.graphics.utils import Color4f, color_to_color4f

from ...config import SelectedAtom
from ...consts import VAO_CUBE_RESOURCE_NAME


class BoundingSphere(Node):
    def __init__(self, config: SelectedAtom, *args, **kwargs):
        super().__init__(*args, **kwargs | dict(node_type=NodeType.TRANSPARENT, visible=False, picking_visible=False))
        self._config = config

        self.set_scale(Vector3D(config.scale_factor, config.scale_factor, config.scale_factor))
        self.set_model(VAO_CUBE_RESOURCE_NAME)
        self.set_color(self._compute_color(config))
        self.set_shader_param("render_mode", 3)
        self.set_shader_param("ray_casting_object", 1)

    def set_config(self, config: SelectedAtom):
        self._config = config
        self.set_color(self._compute_color(config))
        self.set_scale(Vector3D(config.scale_factor, config.scale_factor, config.scale_factor))

    def _compute_color(self, config: SelectedAtom) -> Color4f:
        r, g, b, _ = color_to_color4f(config.color)
        return r, g, b, config.opacity
