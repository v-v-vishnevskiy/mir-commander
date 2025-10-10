from mir_commander.ui.utils.opengl.utils import Color4f

from ..base import BaseGraphicsNode


class Isosurface(BaseGraphicsNode):
    _id_surfacecounter = 0

    def __init__(self, color: Color4f, shader_name: str, *args, **kwargs):
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self.set_color(color)
        self.set_shader(shader_name)

        Isosurface._id_surfacecounter += 1
        self._id_surface = Isosurface._id_surfacecounter

    @property
    def id_surface(self) -> int:
        return self._id_surface
