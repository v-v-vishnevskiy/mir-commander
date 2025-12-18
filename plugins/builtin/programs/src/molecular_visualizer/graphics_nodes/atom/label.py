from mir_commander.core.algebra import Vector3D
from mir_commander.core.graphics.scene.text_node import TextNode
from mir_commander.core.graphics.utils import color_to_color4f

from ...config import AtomLabelConfig


class Label(TextNode):
    def __init__(self, config: AtomLabelConfig, symbol: str, number: int, *args, **kwargs):
        self._size = config.size / 100.0
        self._show_symbol = config.symbol_visible
        self._show_number = config.number_visible
        self._symbol = symbol
        self._number = number

        kwargs["shader_name"] = "atom_label"
        kwargs["color"] = color_to_color4f(config.color)
        kwargs["scale"] = Vector3D(self._size, self._size, self._size)
        super().__init__(*args, **kwargs | dict(visible=config.visible, align="center"))

    def _get_text(self) -> str:
        if self._show_symbol and self._show_number:
            return f"{self._symbol}{self._number}"
        elif self._show_symbol:
            return self._symbol
        elif self._show_number:
            return str(self._number)
        else:
            return ""

    def _update_text(self):
        self.set_text(self._get_text())

    def set_config(self, config: AtomLabelConfig):
        self.set_color(color_to_color4f(config.color))
        s = config.size / 100.0
        self.set_scale(Vector3D(s, s, s))
        self.set_font_atlas_name(config.font)

    def set_visible(self, value: bool, *args, **kwargs):
        if value and not self.children:
            self._update_text()
        super().set_visible(value, *args, **kwargs)

    def set_symbol(self, symbol: str):
        if symbol == self._symbol:
            return
        self._symbol = symbol
        self._update_text()

    def set_number(self, number: int):
        if number == self._number:
            return
        self._number = number
        self._update_text()

    def set_symbol_visible(self, value: bool):
        if value == self._show_symbol:
            return
        self._show_symbol = value
        self._update_text()

    def set_number_visible(self, value: bool):
        if value == self._show_number:
            return
        self._show_number = value
        self._update_text()

    def set_size(self, size: int):
        s = size / 100.0

        if s == self._size:
            return

        self._size = s
        self.set_scale(Vector3D(s, s, s))
