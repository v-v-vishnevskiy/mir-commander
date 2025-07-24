from .base_scene_node import BaseSceneNode
from .base_renderable_node import BaseRenderableNode


class CharNode(BaseRenderableNode):
    node_type = "char"
 
    __slots__ = ("_char",)

    def __init__(self, parent: BaseSceneNode, char: str, visible: bool = True, picking_visible: bool = True):
        super().__init__(parent, visible, picking_visible)

        self._char = char

    def __repr__(self):
        return f"CharNode(id={self._id}, char={self._char})"
