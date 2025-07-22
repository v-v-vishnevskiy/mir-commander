from .base_node import BaseNode


class CharNode(BaseNode):
    node_type = "char"

    __slots__ = ("_char",)

    def __init__(self, char: str, visible: bool, picking_visible: bool):
        super().__init__(visible, picking_visible)

        self._char = char

    def __repr__(self):
        return f"CharNode(id={self._id}, char={self._char})"
