from mir_commander.ui.utils.opengl.resource_manager import SceneNode

from mir_commander.ui.utils.opengl.utils import Color4f, color_to_color4f

from ..config import SelectedAtom


class BoundingSphere(SceneNode):
    def __init__(
        self,
        resource_name: str,
        atom_color: Color4f,
        config: SelectedAtom,
    ):
        super().__init__(transparent=True)
        self._atom_color = atom_color

        self.set_color(self._compute_color(config))
        self.set_mesh(resource_name)
        self.set_vao(resource_name)
        self.set_shader("transparent")

        self.scale(config.scale_factor)

    @property
    def visible(self) -> bool:
        return super().visible and self.parent.selected and not self.parent.cloaked

    def set_config(self, config: SelectedAtom):
        self.set_color(self._compute_color(config))
        self.scale(config.scale_factor)

    def _compute_color(self, config: SelectedAtom) -> Color4f:
        if config.color == "atom":
            color = (self._atom_color[0], self._atom_color[1], self._atom_color[2], config.opacity)
        else:
            r, g, b, _ = color_to_color4f(config.color)
            color = (r, g, b, config.opacity)
        return color
