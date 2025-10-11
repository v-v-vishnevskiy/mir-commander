import numpy as np

from mir_commander.ui.utils.opengl.models.marching_cubes import isosurface
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, compute_smooth_normals

from ...entities import VolumeCubeIsosurface
from ...errors import SurfaceNotFoundError
from .isosurface import Isosurface


class IsosurfaceGroup(Node):
    children: list[Isosurface]  # type: ignore[assignment]

    def __init__(self, resource_manager: ResourceManager, *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._resource_manager = resource_manager

    def add_isosurfaces(self, cube_data: np.ndarray, items: list[tuple[float, Color4f]]) -> list[VolumeCubeIsosurface]:
        isosurfaces = []
        for value, color in items:
            isosurfaces.append(self._add_isosurfaces(cube_data, value, color))
        return isosurfaces

    def _add_isosurfaces(self, cube_data: np.ndarray, value: float, color: Color4f) -> VolumeCubeIsosurface:
        s = Isosurface(parent=self, value=value, color=color, resource_manager=self._resource_manager)
        vertices = isosurface(cube_data, value)
        normals = compute_smooth_normals(vertices)
        model_name = f"isosurface_{s.id}"
        vao = VertexArrayObject(model_name, vertices, normals)
        self._resource_manager.add_vertex_array_object(vao)
        s.set_model(model_name)
        return VolumeCubeIsosurface(id=s.id, value=value, color=color, visible=s.visible)

    def remove(self):
        for s in self.children:
            s.remove()
        super().remove()

    def _get_isosurface(self, id: int) -> Isosurface:
        for surface in self.children:
            if surface.id == id:
                return surface
        raise SurfaceNotFoundError()
