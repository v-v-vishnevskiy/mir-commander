import numpy as np

from mir_commander.ui.utils.opengl.models.marching_cubes import isosurface
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from ...errors import SurfaceNotFoundError
from .isosurface import Isosurface


class IsosurfaceGroup(Node):
    children: list[Isosurface]  # type: ignore[assignment]

    def __init__(self, resource_manager: ResourceManager, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._value = 0.0

        self._resource_manager = resource_manager

    @property
    def value(self) -> float:
        return self._value

    def add_isosurface(self, cube_data: np.ndarray, value: float, color_1: Color4f, color_2: Color4f, inverse: bool):
        self._value = value

        self._add_isosurfaces(cube_data, value, color_1, False)
        if inverse:
            self._add_isosurfaces(cube_data, value, color_2, True)

    def _add_isosurfaces(self, cube_data: np.ndarray, value: float, color: Color4f, inverted: bool):
        s = Isosurface(
            parent=self, value=value, inverted=inverted, color=color, resource_manager=self._resource_manager
        )
        vertices, normals = isosurface(cube_data, value, -1.0 if inverted else 1.0)
        model_name = f"isosurface_{s.id}"
        vao = VertexArrayObject(model_name, vertices, normals)
        self._resource_manager.add_vertex_array_object(vao)
        s.set_model(model_name)

    def remove(self):
        for s in self.children:
            s.remove()
        super().remove()

    def _get_isosurface(self, id: int) -> Isosurface:
        for surface in self.children:
            if surface.id == id:
                return surface
        raise SurfaceNotFoundError()
