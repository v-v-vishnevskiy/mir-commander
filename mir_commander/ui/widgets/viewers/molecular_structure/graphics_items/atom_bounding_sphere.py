from mir_commander.ui.utils.opengl.scene import BaseNode, TransparentNode

from mir_commander.ui.utils.opengl.utils import Color4f, color_to_color4f

from ..config import SelectedAtom


class AtomBoundingSphere(TransparentNode):
    def __init__(
        self,
        parent: BaseNode,
        model_name: str,
        atom_color: Color4f,
        config: SelectedAtom,
    ):
        super().__init__(parent=parent, visible=False, picking_visible=False)
        self._atom_color = atom_color
        self._config = config

        self.set_scale(config.scale_factor)
        self.set_shader("transparent")
        self.set_model(model_name)
        self.set_color(self._compute_color(config))

    def set_config(self, config: SelectedAtom):
        self._config = config
        self.set_color(self._compute_color(config))
        self.set_scale(config.scale_factor)

    def _compute_color(self, config: SelectedAtom) -> Color4f:
        if config.color == "atom":
            color = (self._atom_color[0], self._atom_color[1], self._atom_color[2], config.opacity)
        else:
            r, g, b, _ = color_to_color4f(config.color)
            color = (r, g, b, config.opacity)
        return color
