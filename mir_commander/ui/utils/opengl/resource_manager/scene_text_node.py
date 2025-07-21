from typing import Literal

from .scene_node import SceneNode


class SceneTextNode(SceneNode):
    def __init__(
        self,
        font_atlas_name: str,
        align: Literal["left", "center", "right"] = "left",
        visible: bool = True,
        picking_visible: bool = False,
    ):
        super().__init__(
            is_container=False,
            visible=visible,
            transparent=True,
            picking_visible=picking_visible,
        )
        self._is_text = True
        self._text = ""
        self._font_atlas_name = font_atlas_name
        self._align = align
        self._has_new_text = False

    @property
    def text(self) -> str:
        return self._text

    @property
    def font_atlas_name(self) -> str:
        return self._font_atlas_name

    @property
    def align(self) -> Literal["left", "center", "right"]:
        return self._align

    @property
    def has_new_text(self) -> bool:
        return self._has_new_text

    def set_text(self, text: str):
        self._text = text
        self._has_new_text = True
        self.clear()
        self._build(text)

    def _build(self, text: str):
        for char in text:
            char_node = SceneNode(transparent=True)
            char_node.set_shader(self.shader_name)
            char_node.set_texture(self.texture_name)
            char_node.set_model(f"{self._font_atlas_name}_{char}")
            char_node.set_color(self.color)
            self.add_node(char_node)

    def __repr__(self):
        return f"SceneTextNode(id={self._id}, text={self._text}, font_atlas_name={self._font_atlas_name})"
