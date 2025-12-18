from mir_commander.core.algebra import Quaternion, Vector3D

from ..consts import VAO_CONE_RESOURCE_NAME
from .base import BaseGraphicsNode


class Cone(BaseGraphicsNode):
    def __init__(self, direction: Vector3D, *args, **kwargs):
        self._radius = 1.0
        self._length = 1.0

        kwargs["model_name"] = VAO_CONE_RESOURCE_NAME
        kwargs["shader_params"] = {"lighting_model": 1}
        kwargs["scale"] = Vector3D(self._radius, self._radius, self._length)
        super().__init__(*args, **kwargs)
        self.set_q_rotation(Quaternion.rotation_to(Vector3D(0.0, 0.0, 1.0), direction))

    def set_size(self, radius: float, length: float):
        self._radius = radius
        self._length = length
        self.set_scale(Vector3D(radius, radius, length))
