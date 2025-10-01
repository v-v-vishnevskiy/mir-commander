from mir_commander.ui.utils.opengl.scene import Node, NodeType


class RootNode(Node):
    def __init__(self, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)
