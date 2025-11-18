from typing import Literal

from mir_commander.core.algebra import Vector3D
from mir_commander.core.graphics.font_atlas import FontAtlas
from mir_commander.core.graphics.utils import Color4f

from .node import Node, NodeType


class TextNode(Node):
    __slots__ = ("_text", "_font_atlas_name", "_align")

    def __init__(
        self, font_atlas_name: str = "default", align: Literal["left", "center", "right"] = "center", *args, **kwargs
    ):
        kwargs["node_type"] = NodeType.TEXT
        super().__init__(*args, **kwargs)

        self.set_color((0.0, 0.0, 0.0, 1.0))
        self._modify_children = True

        self._text = ""
        self._font_atlas_name = font_atlas_name
        self._align = align
        self.set_shader("text")

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
        for i, char in enumerate(text):
            char_node = Node(
                parent=self,
                node_type=NodeType.CHAR,
                visible=True,
                picking_visible=self.picking_visible,
            )
            char_node.set_shader(self.shader_name)
            char_node.set_texture(f"font_atlas_{self.font_atlas_name}")
            char_node.set_model(f"font_atlas_{self.font_atlas_name}_{char}")
            char_node.set_color(self._color)
            char_node.metadata["char"] = char
            char_node.metadata["idx"] = i

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
        children = sorted(self.children, key=lambda x: x.metadata["idx"])

        x_offset = 0.0
        for i, char in enumerate(self._text):
            try:
                char_info = font_atlas.chars[char]
            except KeyError:
                char = "?"
                char_info = font_atlas.chars[char]
                child = children[i]
                child.set_model(f"font_atlas_{self.font_atlas_name}_{char}")
            half_width = char_info.width / char_info.height
            x = half_width + x_offset
            children[i].set_position(Vector3D(x, 0.0, 0.0))
            x_offset += half_width * 2

        if self._align == "center":
            vector = Vector3D(-x_offset / 2, 0.0, 0.0)
        elif self._align == "right":
            vector = Vector3D(-x_offset, 0.0, 0.0)
        else:
            vector = Vector3D(0.0, 0.0, 0.0)

        for n in self.children:
            n.translate(vector)

    def __repr__(self):
        return (
            f"TextNode(text={self._text}, font_atlas_name={self._font_atlas_name}, align={self._align}, "
            f"visible={self.visible})"
        )
