from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.graphics_items import MeshItem

from mir_commander.ui.utils.opengl.mesh import Sphere
from mir_commander.ui.utils.opengl.shader import ShaderProgram
from mir_commander.ui.utils.opengl.utils import color_to_color4f

from ..config import SelectedAtom


class BoundingSphere(MeshItem):
    def __init__(
        self,
        mesh_data: Sphere,
        radius: float,
        shader: ShaderProgram,
        config: SelectedAtom,
    ):
        r, g, b, _ = color_to_color4f(config.color)
        super().__init__(mesh_data, color=(r, g, b, config.opacity))
        self.visible = False
        self.picking_visible = False
        self.transparent = True

        self.config = config
        self._compute_transform()

    def _compute_transform(self):
        self._transform.setToIdentity()
        self._transform.scale(self.config.scale_factor, self.config.scale_factor, self.config.scale_factor)
