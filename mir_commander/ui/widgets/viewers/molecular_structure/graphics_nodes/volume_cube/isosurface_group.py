import numpy as np

from mir_commander.ui.utils.opengl.models.marching_cubes import isosurface
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, compute_smooth_normals

from ...errors import SurfaceNotFoundError
from .isosurface import Isosurface


class IsosurfaceGroup(Node):
    children: list[Isosurface]  # type: ignore[assignment]

    def __init__(self, resource_manager: ResourceManager, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._resource_manager = resource_manager

    def add_isosurfaces(self, cube_data: np.ndarray, items: list[tuple[float, Color4f]]) -> list[int]:
        ids = []
        for value, color in items:
            ids.append(self._add_isosurfaces(cube_data, value, color))
        return ids

    def _add_isosurfaces(self, cube_data: np.ndarray, value: float, color: Color4f) -> int:
        s = Isosurface(
            parent=self,
            color=color,
            node_type=NodeType.TRANSPARENT if color[3] < 1.0 else NodeType.OPAQUE,
            shader_name="transparent" if color[3] < 1.0 else "default",
        )
        vertices = isosurface(cube_data, value)
        normals = compute_smooth_normals(vertices)
        model_name = f"isosurface_{s.id}"
        vao = VertexArrayObject(model_name, vertices, normals)
        self._resource_manager.add_vertex_array_object(vao)
        s.set_model(model_name)
        return s.id

    def remove(self):
        for s in self.children:
            s.remove()
            self._resource_manager.remove_vertex_array_object(s.model_name)
        super().remove()

    def remove_isosurface(self, id: int):
        try:
            s = self._get_isosurface(id)
            s.remove()
            self._resource_manager.remove_vertex_array_object(s.model_name)
        except SurfaceNotFoundError:
            pass

        if len(self.children) == 0:
            self.remove()

    def _get_isosurface(self, id: int) -> Isosurface:
        for surface in self.children:
            if surface.id == id:
                return surface
        raise SurfaceNotFoundError()
