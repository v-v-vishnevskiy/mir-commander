from mir_commander.core.algebra import Vector3D

from ..consts import VAO_CUBE_RESOURCE_NAME
from .base import BaseGraphicsNode


class Sphere(BaseGraphicsNode):
    def __init__(self, radius: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = radius
        self.set_scale(Vector3D(radius, radius, radius))
        self.set_model(VAO_CUBE_RESOURCE_NAME)
        self.set_shader_param("lighting_model", 1)
        self.set_shader_param("render_mode", 3)
        self.set_shader_param("ray_casting_object", 1)

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(Vector3D(radius, radius, radius))
