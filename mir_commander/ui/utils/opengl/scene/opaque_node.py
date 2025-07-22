from .base_node import BaseNode


class OpaqueNode(BaseNode):
    node_type = "opaque"

    def __init__(self, visible: bool, picking_visible: bool):
        super().__init__(visible, picking_visible)
