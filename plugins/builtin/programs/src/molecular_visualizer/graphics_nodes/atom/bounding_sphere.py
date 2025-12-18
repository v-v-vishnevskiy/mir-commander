from mir_commander.core.algebra import Vector3D
from mir_commander.core.graphics.scene.node import Node, NodeType
from mir_commander.core.graphics.utils import Color4f, color_to_color4f

from ...config import SelectedAtom
from ...consts import VAO_CUBE_RESOURCE_NAME


class BoundingSphere(Node):
    def __init__(self, config: SelectedAtom, *args, **kwargs):
        kwargs["model_name"] = VAO_CUBE_RESOURCE_NAME
        kwargs["shader_params"] = {"render_mode": 3, "ray_casting_object": 1}
        kwargs["color"] = self._compute_color(config)
        kwargs["scale"] = Vector3D(config.scale_factor, config.scale_factor, config.scale_factor)
        super().__init__(*args, **kwargs | dict(node_type=NodeType.TRANSPARENT, visible=False, picking_visible=False))
        self._config = config

    def set_config(self, config: SelectedAtom):
        self._config = config
        self.set_color(self._compute_color(config))
        self.set_scale(Vector3D(config.scale_factor, config.scale_factor, config.scale_factor))

    def _compute_color(self, config: SelectedAtom) -> Color4f:
        r, g, b, _ = color_to_color4f(config.color)
        return r, g, b, config.opacity
