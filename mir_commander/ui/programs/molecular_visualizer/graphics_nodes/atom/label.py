from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import TextNode
from mir_commander.ui.utils.opengl.utils import color_to_color4f

from ...config import AtomLabelConfig


class Label(TextNode):
    def __init__(self, config: AtomLabelConfig, symbol: str, number: int, *args, **kwargs):
        super().__init__(*args, **kwargs | dict(visible=config.visible, align="center"))

        self._show_symbol = config.symbol_visible
        self._show_number = config.number_visible
        self._symbol = symbol
        self._number = number

        self._size = config.size / 100.0
        self.set_scale(QVector3D(self._size, self._size, self._size))
        self.set_shader("atom_label")
        self.set_color(color_to_color4f(config.color))
        self._update_text()

    def _update_text(self):
        if self._show_symbol and self._show_number:
            self.set_text(f"{self._symbol}{self._number}")
        elif self._show_symbol:
            self.set_text(self._symbol)
        elif self._show_number:
            self.set_text(str(self._number))
        else:
            self.set_text("")

    def set_config(self, config: AtomLabelConfig):
        self.set_color(color_to_color4f(config.color))
        s = config.size / 100.0
        self.set_scale(QVector3D(s, s, s))
        self.set_font_atlas_name(config.font)

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
        self.set_scale(QVector3D(s, s, s))
