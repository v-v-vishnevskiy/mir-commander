from PySide6.QtGui import QVector3D

from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from ...errors import SurfaceNotFoundError
from .surface import Surface


class VolumeCube(Node):
    children: list[Surface]  # type: ignore[assignment]

    def __init__(self, volume_cube: CoreVolumeCube = CoreVolumeCube(), *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

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

        x, y, z = self._volume_cube.find_points_xyz(value)
        points = [QVector3D(x, y, z) for x, y, z in zip(x, y, z)]
        Surface(parent=self, value=value, points=points, color=color)

    def remove_surface(self, value: float):
        try:
            s = self.find_surface(value)
            s.remove()
        except SurfaceNotFoundError:
            pass

    def find_surface(self, value: float) -> Surface:
        for surface in self.children:
            if surface.value == value:
                return surface
        raise SurfaceNotFoundError()
