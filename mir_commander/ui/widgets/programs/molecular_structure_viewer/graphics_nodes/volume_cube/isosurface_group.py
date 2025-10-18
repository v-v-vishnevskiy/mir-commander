import numpy as np

from mir_commander.ui.utils.opengl.models import marching_cubes
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from .isosurface import Isosurface


class IsosurfaceGroup(Node):
    children: list[Isosurface]  # type: ignore[assignment]

    def __init__(
        self,
        value: float,
        cube_data: np.ndarray,
        color_1: Color4f,
        color_2: Color4f,
        inverse: bool,
        resource_manager: ResourceManager,
        *args,
        **kwargs,
    ):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._value = value
        self._resource_manager = resource_manager

        self._add_isosurfaces(cube_data, value, color_1, False)
        if inverse:
            self._add_isosurfaces(cube_data, value, color_2, True)

    @property
    def value(self) -> float:
        return self._value

    def _add_isosurfaces(self, cube_data: np.ndarray, value: float, color: Color4f, inverted: bool):
        isosurface = Isosurface(parent=self, inverted=inverted, color=color, resource_manager=self._resource_manager)
        vertices, normals = marching_cubes.isosurface(cube_data, value, -1.0 if inverted else 1.0)
        model_name = f"isosurface_{isosurface.id}"
        vao = VertexArrayObject(model_name, vertices, normals)
        self._resource_manager.add_vertex_array_object(vao)
        isosurface.set_model(model_name)

    def remove(self):
        for isosurface in self.children:
            isosurface.remove()
        super().remove()
