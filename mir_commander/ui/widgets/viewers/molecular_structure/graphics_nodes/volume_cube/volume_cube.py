from PySide6.QtGui import QVector3D

from mir_commander.core.models import VolumeCube as CoreVolumeCube
from mir_commander.ui.utils.opengl.scene import Node, NodeType

from .sphere import Sphere


class VolumeCube(Node):
    def __init__(self, volume_cube: CoreVolumeCube = CoreVolumeCube(), *args, **kwargs):
        kwargs["node_type"] = NodeType.CONTAINER
        kwargs["visible"] = True
        super().__init__(*args, **kwargs)

        self._volume_cube = volume_cube

    def set_volume_cube(self, volume_cube: CoreVolumeCube):
        self.clear()
        self._volume_cube = volume_cube

    def build(self, value: float):
        self.clear()

        x, y, z = self._volume_cube.find_points_xyz(value)
        for i in range(len(x)):
            Sphere(parent=self, position=QVector3D(x[i], y[i], z[i]))
