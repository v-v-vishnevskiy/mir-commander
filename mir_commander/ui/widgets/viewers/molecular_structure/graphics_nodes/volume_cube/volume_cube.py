from PySide6.QtGui import QVector3D

from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.models.marching_cubes import isosurface
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, compute_smooth_normals
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

    @property
    def isosurfaces(self) -> list[tuple[float, Color4f]]:
        return [(s.value, s.color) for s in self.children]

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        position = QVector3D(volume_cube.box_origin[0], volume_cube.box_origin[1], volume_cube.box_origin[2])
        self.set_translation(position * consts.BOHR2ANGSTROM)

        scale = QVector3D(volume_cube.steps_size[0][0], volume_cube.steps_size[1][1], volume_cube.steps_size[2][2])
        self.set_scale(scale * consts.BOHR2ANGSTROM)

        for s in self.children:
            s.remove()
            self._resource_manager.remove_vertex_array_object(s.vao_name)
        self._volume_cube = volume_cube

    def add_isosurface(self, value: float, color: Color4f):
        try:
            s = self.find_isosurface(value)
            s.remove()
        except SurfaceNotFoundError:
            pass

        vertices = isosurface(self._volume_cube.cube_data, value)
        normals = compute_smooth_normals(vertices)
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
