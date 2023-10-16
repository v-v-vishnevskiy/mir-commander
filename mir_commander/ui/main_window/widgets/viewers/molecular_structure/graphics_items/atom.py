from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.graphics_items import MeshItem
from mir_commander.ui.utils.opengl.mesh import Sphere
from mir_commander.ui.utils.opengl.utils import Color4f


class Atom(MeshItem):
    def __init__(self, mesh_data: Sphere, atomic_num: int, position: QVector3D, radius: float, color: Color4f):
        super().__init__(mesh_data, color=color)
        self.position = position
        self.radius = radius
        self.atomic_num = atomic_num

        self._compute_transform()

    def _compute_transform(self):
        self.transform.setToIdentity()
        self.transform.translate(self.position)
        self.transform.scale(self.radius, self.radius, self.radius)

    def set_radius(self, radius: float):
        self.radius = radius
        self._compute_transform()

    def set_position(self, position: QVector3D):
        self.position = position
        self._compute_transform()
