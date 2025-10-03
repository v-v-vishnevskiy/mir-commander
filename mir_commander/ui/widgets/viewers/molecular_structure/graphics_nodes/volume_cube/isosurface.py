from mir_commander.ui.utils.opengl.utils import Color4f

from ..base import BaseGraphicsNode


class Isosurface(BaseGraphicsNode):
    def __init__(self, value: float, vao_name: str, color: Color4f, *args, **kwargs):
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._value = value
        self._vao_name = vao_name
        self._color = color

        self.set_color(self._color)
        self.set_model(self._vao_name)
        self.set_shader("default")

    @property
    def value(self) -> float:
        return self._value

    @property
    def vao_name(self) -> str:
        return self._vao_name
