from PySide6.QtGui import QVector3D

from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f
from mir_commander.utils import consts

from ...entities import VolumeCubeIsosurface, VolumeCubeIsosurfaceGroup
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

    @property
    def is_empty_scalar_field(self) -> bool:
        return self._volume_cube.cube_data is None or self._volume_cube.cube_data.size == 0

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        position = QVector3D(volume_cube.box_origin[0], volume_cube.box_origin[1], volume_cube.box_origin[2])
        self.set_translation(position * consts.BOHR2ANGSTROM)

        scale = QVector3D(volume_cube.steps_size[0][0], volume_cube.steps_size[1][1], volume_cube.steps_size[2][2])
        self.set_scale(scale * consts.BOHR2ANGSTROM)

        for s in self.children:
            s.remove()
        self._volume_cube = volume_cube

    def add_isosurface(self, value: float, color_1: Color4f, color_2: Color4f, inverse: bool) -> bool:
        if self.is_empty_scalar_field:
            return False

        group = IsosurfaceGroup(parent=self, resource_manager=self._resource_manager)
        group.add_isosurface(self._volume_cube.cube_data, value, color_1, color_2, inverse)
        return True

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

    @property
    def isosurface_groups(self) -> list[VolumeCubeIsosurfaceGroup]:
        result = []
        for group in self.children:
            isosurfaces = []
            for s in group.children:
                isosurfaces.append(
                    VolumeCubeIsosurface(id=s.id, value=s.value, inverted=s.inverted, color=s.color, visible=s.visible)
                )
            result.append(
                VolumeCubeIsosurfaceGroup(
                    id=group.id, value=group.value, isosurfaces=isosurfaces, visible=any(s.visible for s in isosurfaces)
                )
            )
        return result
