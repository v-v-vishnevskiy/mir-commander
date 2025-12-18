from mir_commander.core.algebra import Quaternion, Vector3D

from ..consts import VAO_CUBE_RESOURCE_NAME
from .base import BaseGraphicsNode


class Cylinder(BaseGraphicsNode):
    def __init__(self, direction: Vector3D, length: float, radius: float, *args, **kwargs):
        self._length = length / 2
        self._radius = radius
        self._direction = direction

        kwargs["model_name"] = VAO_CUBE_RESOURCE_NAME
        kwargs["shader_params"] = {"lighting_model": 1, "render_mode": 3, "ray_casting_object": 2}
        kwargs["scale"] = Vector3D(self._radius, self._radius, self._length)
        kwargs["position"] = self._compute_position(kwargs.get("position", Vector3D(0.0, 0.0, 0.0)))
        kwargs["rotation"] = Quaternion.rotation_to(Vector3D(0.0, 0.0, 1.0), self._direction)
        super().__init__(*args, **kwargs)

    def _compute_position(self, value: Vector3D) -> Vector3D:
        return value + self._direction * self._length

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
        super().set_position(self._compute_position(value))
