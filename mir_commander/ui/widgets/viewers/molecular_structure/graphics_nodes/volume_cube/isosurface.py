from typing import TYPE_CHECKING

from mir_commander.ui.utils.opengl.resource_manager import ResourceManager
from mir_commander.ui.utils.opengl.utils import Color4f

from ..base import BaseGraphicsNode

if TYPE_CHECKING:
    from .isosurface_group import IsosurfaceGroup


class Isosurface(BaseGraphicsNode):
    parent: "IsosurfaceGroup"  # type: ignore[assignment]

    def __init__(
        self, value: float, color: Color4f, shader_name: str, resource_manager: ResourceManager, *args, **kwargs
    ):
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._value = value
        self._resource_manager = resource_manager

        self.set_color(color)
        self.set_shader(shader_name)

    @property
    def value(self) -> float:
        return self._value

    def remove(self):
        parent = self.parent

        self._resource_manager.remove_vertex_array_object(self.model_name)
        super().remove()

        if len(parent.children) == 0:
            parent.remove()
