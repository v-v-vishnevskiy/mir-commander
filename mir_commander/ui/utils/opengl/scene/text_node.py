from typing import Literal

from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager.font_atlas import FontAtlas
from mir_commander.ui.utils.opengl.utils import Color4f

from .node import Node, NodeType


class TextNode(Node):
    __slots__ = ("_text", "_font_atlas_name", "_align")

    def __init__(
        self,
        parent: Node,
        visible: bool = True,
        picking_visible: bool = False,
        font_atlas_name: str = "default",
        align: Literal["left", "center", "right"] = "center",
    ):
        super().__init__(parent=parent, node_type=NodeType.TEXT, visible=visible, picking_visible=picking_visible)
        self.set_color((0.0, 0.0, 0.0, 1.0))
        self._modify_children = True

        self._text = ""
        self._font_atlas_name = font_atlas_name
        self._align = align

    @property
    def text(self) -> str:
        return self._text

    @property
    def font_atlas_name(self) -> str:
        return self._font_atlas_name

    @property
    def align(self) -> str:
        return self._align

    def _build(self, text: str):
        for char in text:
            char_node = Node(
                parent=self,
                node_type=NodeType.CHAR,
                visible=self.visible,
                picking_visible=self.picking_visible,
            )
            char_node.set_shader(self.shader_name)
            char_node.set_texture(f"font_atlas_{self.font_atlas_name}")
            char_node.set_model(f"font_atlas_{self.font_atlas_name}_{char}")
            char_node.set_color(self._color)
            char_node.metadata["char"] = char

    def set_text(self, text: str):
        self._text = text
        self.clear()
        self._build(text)
        self._root_node.notify_add_node(self)

    def set_font_atlas_name(self, name: str):
        if self._font_atlas_name == name:
            return

        self._font_atlas_name = name
        for node in self.children:
            node.set_texture(f"font_atlas_{name}")
        self._root_node.notify_add_node(self)

    def set_shader(self, name: str):
        self._shader_name = name
        for node in self.children:
            node.set_shader(name)

    def set_color(self, color: Color4f):
        self._color = color
        for node in self.children:
            node.set_color(color)

    def update_char_translation(self, font_atlas: FontAtlas):
        x_offset = 0.0
        children = self.children

        x_offset = 0.0
        for i, char in enumerate(self._text):
            char_info = font_atlas.chars[char]
            half_width = char_info.width / char_info.height
            x = half_width + x_offset
            children[i].set_translation(QVector3D(x, 0.0, 0.0))
            x_offset += half_width * 2

        if self._align == "center":
            vector = QVector3D(-x_offset / 2, 0.0, 0.0)
        elif self._align == "right":
            vector = QVector3D(-x_offset, 0.0, 0.0)
        else:
            vector = QVector3D(0.0, 0.0, 0.0)

        for n in children:
            n.translate(vector)

    def __repr__(self):
        return f"TextNode(text={self._text}, font_atlas_name={self._font_atlas_name}, align={self._align})"
