from mir_commander.ui.utils.opengl.graphics_items import MeshItem

from mir_commander.ui.utils.opengl.mesh import Sphere
from mir_commander.ui.utils.opengl.utils import Color4f, color_to_color4f

from ..config import SelectedAtom


class BoundingSphere(MeshItem):
    def __init__(
        self,
        mesh_data: Sphere,
        radius: float,
        atom_color: Color4f,
        config: SelectedAtom,
    ):
        self.atom_color = atom_color
        super().__init__(mesh_data, color=self._compute_color(config))
        self.picking_visible = False
        self.transparent = True

        self.config = config
        self._compute_transform()

    @property
    def visible(self) -> bool:
        return super().visible and self.parent.selected and not self.parent.cloaked

    def set_config(self, config: SelectedAtom):
        self.config = config
        self.set_color(self._compute_color(config))
        self._compute_transform()

    def _compute_color(self, config: SelectedAtom) -> Color4f:
        if config.color == "atom":
            color = (self.atom_color[0], self.atom_color[1], self.atom_color[2], config.opacity)
        else:
            r, g, b, _ = color_to_color4f(config.color)
            color = (r, g, b, config.opacity)
        return color

    def _compute_transform(self):
        self._transform.setToIdentity()
        self._transform.scale(self.config.scale_factor, self.config.scale_factor, self.config.scale_factor)
