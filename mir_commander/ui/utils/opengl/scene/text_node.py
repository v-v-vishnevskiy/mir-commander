from typing import Literal

from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager.font_atlas import FontAtlasInfo
from mir_commander.ui.utils.opengl.utils import Color4f

from .char_node import CharNode
from .base_renderable_node import BaseRenderableNode
from .base_node import BaseNode


class TextNode(BaseRenderableNode):
    node_type = "text"

    __slots__ = ("_picking_visible", "_font_atlas_name", "_align", "_text", "_has_new_text")

    def __init__(
        self,
        parent: BaseNode,
        visible: bool,
        picking_visible: bool,
        font_atlas_name: str,
        align: Literal["left", "center", "right"],
    ):
        self._font_atlas_name = font_atlas_name
        self._align = align
        self._text = ""
        self._has_new_text = False

        super().__init__(parent, visible, picking_visible)
        self._modify_children = True

    @property
    def text(self) -> str:
        return self._text

    @property
    def font_atlas_name(self) -> str:
        return self._font_atlas_name

    @property
    def align(self) -> str:
        return self._align

    @property
    def has_new_text(self) -> bool:
        return self._has_new_text

    def _build(self, text: str):
        for char in text:
            char_node = CharNode(parent=self, char=char, visible=self.visible, picking_visible=self._picking_visible)
            char_node.set_shader(self.shader_name)
            char_node.set_texture(self.texture_name)
            char_node.set_model(f"{self._font_atlas_name}_{char}")
            char_node.set_color(self._color)

    def set_text(self, text: str):
        self._text = text
        self._has_new_text = True
        self.clear()
        self._build(text)

    def set_color(self, color: Color4f):
        self._color = color
        for node in self.children:
            node.set_color(color)

    def update_char_translation(self, font_atlas_info: FontAtlasInfo):
        x_offset = 0.0
        children = self.children

        x_offset = 0.0
        for i, char in enumerate(self._text):
            char_info = font_atlas_info.chars[char]
            half_width = char_info.width / char_info.height
            x = half_width + x_offset
            children[i].translate(QVector3D(x, 0.0, 0.0))
            x_offset += half_width * 2

        if self._align == "center":
            vector = QVector3D(-x_offset / 2, 0.0, 0.0)
        elif self._align == "right":
            vector = QVector3D(-x_offset, 0.0, 0.0)
        else:
            vector = QVector3D(0.0, 0.0, 0.0)

        for n in children:
            n.translate(vector)

        self._has_new_text = False

    def __repr__(self):
        return f"TextNode(text={self._text}, font_atlas_name={self._font_atlas_name})"
