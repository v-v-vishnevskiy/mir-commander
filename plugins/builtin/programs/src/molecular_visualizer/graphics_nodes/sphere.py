from mir_commander.core.algebra import Vector3D

from ..consts import VAO_CUBE_RESOURCE_NAME
from .base import BaseGraphicsNode


class Cube(BaseGraphicsNode):
    def __init__(self, radius: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = radius
        self.set_scale(Vector3D(radius, radius, radius))
        self.set_model(VAO_CUBE_RESOURCE_NAME)

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(Vector3D(radius, radius, radius))
