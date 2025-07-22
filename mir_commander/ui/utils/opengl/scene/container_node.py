from .base_node import BaseNode


class ContainerNode(BaseNode):
    node_type = "container"

    def __init__(self, visible: bool):
        super().__init__(visible, picking_visible=False)
