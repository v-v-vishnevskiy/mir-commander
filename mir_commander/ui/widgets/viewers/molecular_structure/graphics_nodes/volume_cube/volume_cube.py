from PySide6.QtGui import QVector3D

from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f
from mir_commander.utils import consts

from ...errors import SurfaceNotFoundError
from .isosurface_group import IsosurfaceGroup


class VolumeCube(Node):
    children: list[IsosurfaceGroup]  # type: ignore[assignment]

    def __init__(
        self, resource_manager: ResourceManager, volume_cube: CoreVolumeCube = CoreVolumeCube(), *args, **kwargs
    ):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._resource_manager = resource_manager

        self._volume_cube = volume_cube

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        position = QVector3D(volume_cube.box_origin[0], volume_cube.box_origin[1], volume_cube.box_origin[2])
        self.set_translation(position * consts.BOHR2ANGSTROM)

        scale = QVector3D(volume_cube.steps_size[0][0], volume_cube.steps_size[1][1], volume_cube.steps_size[2][2])
        self.set_scale(scale * consts.BOHR2ANGSTROM)

        for s in self.children:
            s.remove()
        self._volume_cube = volume_cube

    def add_isosurface_group(self, items: list[tuple[float, Color4f]]) -> int:
        group = IsosurfaceGroup(parent=self, resource_manager=self._resource_manager)
        group.add_isosurfaces(self._volume_cube.cube_data, items)
        return group.id

    def remove_isosurface_group(self, id: int):
        try:
            self.get_isosurface_group(id).remove()
        except SurfaceNotFoundError:
            pass

    def get_isosurface_group(self, id: int) -> IsosurfaceGroup:
        for group in self.children:
            if group.id == id:
                return group
        raise SurfaceNotFoundError()
