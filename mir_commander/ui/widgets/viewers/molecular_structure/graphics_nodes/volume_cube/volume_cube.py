from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.models.isosurface import marching_cubes
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, compute_vertex_normals
from mir_commander.utils import consts

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
        self._scalar_field = self._prepare_scalar_field()

    def _prepare_scalar_field(self):
        if len(self._volume_cube.steps_number) == 0:
            return []

        result: list[list[list[tuple[float, float, float, float]]]] = []
        for i in range(self._volume_cube.steps_number[0]):
            for j in range(self._volume_cube.steps_number[1]):
                for k in range(self._volume_cube.steps_number[2]):
                    value = self._volume_cube.cube_data[i][j][k]
                    x = (
                        self._volume_cube.steps_size[0][0] * i
                        + self._volume_cube.steps_size[0][1] * j
                        + self._volume_cube.steps_size[0][2] * k
                        + self._volume_cube.box_origin[0]
                    ) * consts.BOHR2ANGSTROM
                    y = (
                        self._volume_cube.steps_size[1][0] * i
                        + self._volume_cube.steps_size[1][1] * j
                        + self._volume_cube.steps_size[1][2] * k
                        + self._volume_cube.box_origin[1]
                    ) * consts.BOHR2ANGSTROM
                    z = (
                        self._volume_cube.steps_size[2][0] * i
                        + self._volume_cube.steps_size[2][1] * j
                        + self._volume_cube.steps_size[2][2] * k
                        + self._volume_cube.box_origin[2]
                    ) * consts.BOHR2ANGSTROM
                    if len(result) < i + 1:
                        result.append([])
                    if len(result[i]) < j + 1:
                        result[i].append([])
                    result[i][j].append((x, y, z, value))
        return result

    @property
    def isosurfaces(self) -> list[tuple[float, Color4f]]:
        return [(s.value, s.color) for s in self.children]

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        self.clear()
        self._volume_cube = volume_cube
        self._scalar_field = self._prepare_scalar_field()

    def add_isosurface(self, value: float, color: Color4f):
        try:
            s = self.find_isosurface(value)
            s.remove()
        except SurfaceNotFoundError:
            pass

        vertices = marching_cubes(self._scalar_field, value)
        normals = compute_vertex_normals(vertices)
        vao_name = f"isosurface_{value}"
        vao = VertexArrayObject(vao_name, vertices, normals)
        self._resource_manager.add_vertex_array_object(vao)
        Isosurface(parent=self, value=value, vao_name=vao_name, color=color)

    def remove_isosurface(self, value: float):
        try:
            s = self.find_isosurface(value)
            s.remove()
            self._resource_manager.remove_vertex_array_object(s.vao_name)
        except SurfaceNotFoundError:
            pass

    def find_isosurface(self, value: float) -> Isosurface:
        for surface in self.children:
            if surface.value == value:
                return surface
        raise SurfaceNotFoundError()
