from .base_scene_node import BaseSceneNode
from .base_renderable_node import BaseRenderableNode


class CharNode(BaseRenderableNode):
    node_type = "char"
 
    __slots__ = ("_char",)

    def __init__(self, parent: BaseSceneNode, char: str, visible: bool, picking_visible: bool):
        self._char = char

        super().__init__(parent, visible, picking_visible)

    def __repr__(self):
        return f"CharNode(id={self._id}, char={self._char})"
