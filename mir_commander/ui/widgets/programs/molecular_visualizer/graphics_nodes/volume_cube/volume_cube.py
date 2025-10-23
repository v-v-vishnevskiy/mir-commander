from PySide6.QtGui import QVector3D

from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.resource_manager import ResourceManager
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f
from mir_commander.utils import consts

from ...entities import VolumeCubeIsosurface, VolumeCubeIsosurfaceGroup
from ...errors import EmptyScalarFieldError, SurfaceNotFoundError
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
        self.set_position(position * consts.BOHR2ANGSTROM)

        scale = QVector3D(volume_cube.steps_size[0][0], volume_cube.steps_size[1][1], volume_cube.steps_size[2][2])
        self.set_scale(scale * consts.BOHR2ANGSTROM)

        for s in self.children:
            s.remove()
        self._volume_cube = volume_cube

    def add_isosurface(
        self, value: float, color_1: Color4f, color_2: Color4f, inverse: bool
    ) -> VolumeCubeIsosurfaceGroup:
        if self.is_empty_scalar_field:
            raise EmptyScalarFieldError()

        group = IsosurfaceGroup(
            parent=self,
            resource_manager=self._resource_manager,
            value=value,
            cube_data=self._volume_cube.cube_data,
            color_1=color_1,
            color_2=color_2,
            inverse=inverse,
        )
        return self._group_node_to_entity(group)

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
        return [self._group_node_to_entity(group) for group in self.children]

    def _group_node_to_entity(self, group: IsosurfaceGroup) -> VolumeCubeIsosurfaceGroup:
        return VolumeCubeIsosurfaceGroup(
            id=group.id,
            value=group.value,
            isosurfaces=[
                VolumeCubeIsosurface(
                    id=isosurface.id, inverted=isosurface.inverted, color=isosurface.color, visible=isosurface.visible
                )
                for isosurface in group.children
            ],
            visible=any(isosurface.visible for isosurface in group.children),
        )
