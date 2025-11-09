import math
from copy import copy

import numpy as np

from mir_commander.ui.sdk.opengl.models import marching_cubes
from mir_commander.ui.sdk.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.sdk.opengl.scene import Node, NodeType
from mir_commander.ui.sdk.opengl.utils import Color4f

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
        unique_id: int,
        resource_manager: ResourceManager,
        *args,
        **kwargs,
    ):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._value = math.fabs(value)
        self._unique_id = unique_id
        self._resource_manager = resource_manager

        self._add_isosurfaces(cube_data, math.fabs(value), color_1, value < 0, self._unique_id + 1)
        if inverse and value != 0.0:
            self._add_isosurfaces(cube_data, math.fabs(value), color_2, value > 0, self._unique_id + 2)

    @property
    def value(self) -> float:
        return self._value

    @property
    def unique_id(self) -> int:
        return self._unique_id

    def _add_isosurfaces(self, cube_data: np.ndarray, value: float, color: Color4f, inverted: bool, unique_id: int):
        isosurface = Isosurface(
            parent=self,
            inverted=inverted,
            color=color,
            resource_manager=self._resource_manager,
            unique_id=unique_id,
        )
        vertices, normals = marching_cubes.isosurface(cube_data, value, -1.0 if inverted else 1.0)
        model_name = f"isosurface_{isosurface.id}"
        vao = VertexArrayObject(model_name, vertices, normals)
        self._resource_manager.add_vertex_array_object(vao)
        isosurface.set_model(model_name)

    def remove(self):
        for isosurface in copy(self.children):
            isosurface.remove()
        super().remove()
