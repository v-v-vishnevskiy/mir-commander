from mir_commander.core.algebra import Quaternion, Vector3D

from ..consts import VAO_CYLINDER_RESOURCE_NAME
from .base import BaseGraphicsNode


class Cylinder(BaseGraphicsNode):
    def __init__(self, direction: Vector3D, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = 1.0
        self._length = 1.0
        self._direction = direction.normalized
        self.set_model(VAO_CYLINDER_RESOURCE_NAME)
        self.set_q_rotation(Quaternion.rotation_to(Vector3D(0.0, 0.0, 1.0), self._direction))
        self.set_scale(Vector3D(self._radius, self._radius, self._length))

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(Vector3D(self._radius, self._radius, self._length))

    def set_length(self, length: float):
        self._length = length / 2
        self.set_scale(Vector3D(self._radius, self._radius, self._length))

    def set_size(self, radius: float, length: float):
        self._radius = radius
        self._length = length / 2
        self.set_scale(Vector3D(self._radius, self._radius, self._length))

    def set_position(self, value: Vector3D):
        super().set_position(value + self._direction * self._length)
