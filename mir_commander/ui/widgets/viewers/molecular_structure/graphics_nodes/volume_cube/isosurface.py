from mir_commander.ui.utils.opengl.utils import Color4f

from ..base import BaseGraphicsNode


class Isosurface(BaseGraphicsNode):
    def __init__(self, color: Color4f, shader_name: str, *args, **kwargs):
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self.set_color(color)
        self.set_shader(shader_name)
