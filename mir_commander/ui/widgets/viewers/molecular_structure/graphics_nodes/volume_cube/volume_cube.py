from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.models.isosurface import marching_cubes
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, compute_vertex_normals

from ...errors import SurfaceNotFoundError
from .isosurface import Isosurface


class VolumeCube(Node):
    children: list[Isosurface]  # type: ignore[assignment]

    def __init__(
        self, resource_manager: ResourceManager, volume_cube: CoreVolumeCube = CoreVolumeCube(), *args, **kwargs
    ):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._resource_manager = resource_manager

        self._volume_cube = volume_cube

    @property
    def surfaces(self) -> list[tuple[float, Color4f]]:
        return [(s.value, s.color) for s in self.children]

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        self.clear()
        self._volume_cube = volume_cube

    def add_surface(self, value: float, color: Color4f):
        try:
            s = self.find_surface(value)
            s.remove()
        except SurfaceNotFoundError:
            pass

        vertices = marching_cubes(
            self._volume_cube.steps_size, self._volume_cube.box_origin, self._volume_cube.cube_data, value
        )
        normals = compute_vertex_normals(vertices)
        vao_name = f"isosurface_{value}"
        vao = VertexArrayObject(vao_name, vertices, normals)
        self._resource_manager.add_vertex_array_object(vao)
        Isosurface(parent=self, value=value, vao_name=vao_name, color=color)

    def remove_surface(self, value: float):
        try:
            s = self.find_surface(value)
            s.remove()
            self._resource_manager.remove_vertex_array_object(s.vao_name)
        except SurfaceNotFoundError:
            pass

    def find_surface(self, value: float) -> Isosurface:
        for surface in self.children:
            if surface.value == value:
                return surface
        raise SurfaceNotFoundError()
