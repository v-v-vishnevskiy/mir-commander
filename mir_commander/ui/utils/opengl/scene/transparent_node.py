from .base_node import BaseNode


class TransparentNode(BaseNode):
    node_type = "transparent"

    def __init__(self, visible: bool, picking_visible: bool):
        super().__init__(visible, picking_visible)
