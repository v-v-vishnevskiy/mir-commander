from mir_commander.ui.utils.opengl.scene import NodeType

from ..base import BaseGraphicsNode


class Sphere(BaseGraphicsNode):
    def __init__(self, *args, **kwargs):
        kwargs["node_type"] = NodeType.TRANSPARENT
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)
