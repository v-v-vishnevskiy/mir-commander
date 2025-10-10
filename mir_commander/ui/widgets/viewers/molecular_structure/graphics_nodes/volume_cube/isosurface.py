from mir_commander.ui.utils.opengl.utils import Color4f

from ..base import BaseGraphicsNode


class Isosurface(BaseGraphicsNode):
    _counter = 0

    def __init__(self, color: Color4f, shader_name: str, *args, **kwargs):
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self.set_color(color)
        self.set_shader(shader_name)

        Isosurface._counter += 1
        self._surface_id = Isosurface._counter

    @property
    def surface_id(self) -> int:
        return self._surface_id
