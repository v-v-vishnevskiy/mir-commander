from typing import TYPE_CHECKING

from mir_commander.ui.sdk.opengl.resource_manager import ResourceManager
from mir_commander.ui.sdk.opengl.scene import NodeType
from mir_commander.ui.sdk.opengl.utils import Color4f

from ..base import BaseGraphicsNode

if TYPE_CHECKING:
    from .isosurface_group import IsosurfaceGroup


class Isosurface(BaseGraphicsNode):
    parent: "IsosurfaceGroup"  # type: ignore[assignment]

    def __init__(
        self, inverted: bool, color: Color4f, unique_id: int, resource_manager: ResourceManager, *args, **kwargs
    ):
        kwargs["visible"] = True
        kwargs["node_type"] = NodeType.TRANSPARENT if color[3] < 1.0 else NodeType.OPAQUE
        super().__init__(*args, **kwargs)

        self._inverted = inverted
        self._unique_id = unique_id
        self._resource_manager = resource_manager

        self.set_color(color)
        self.set_shader("transparent" if color[3] < 1.0 else "default")

    @property
    def inverted(self) -> bool:
        return self._inverted

    @property
    def unique_id(self) -> int:
        return self._unique_id

    def set_color(self, color: Color4f):
        super().set_color(color)
        self.set_node_type(NodeType.TRANSPARENT if color[3] < 1.0 else NodeType.OPAQUE)
        self.set_shader("transparent" if color[3] < 1.0 else "default")

    def remove(self):
        parent = self.parent

        self._resource_manager.remove_vertex_array_object(self.model_name)
        super().remove()

        if len(parent.children) == 0:
            parent.remove()
