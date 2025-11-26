from mir_commander.core.algebra import Vector3D

from ..consts import VAO_CUBE_RESOURCE_NAME
from .base import BaseGraphicsNode


class Sphere(BaseGraphicsNode):
    def __init__(self, radius: float, *args, **kwargs):
        kwargs["model_name"] = VAO_CUBE_RESOURCE_NAME
        kwargs["shader_params"] = {"lighting_model": 1, "render_mode": 3, "ray_casting_object": 1}
        kwargs["scale"] = Vector3D(radius, radius, radius)
        super().__init__(*args, **kwargs)
        self._radius = radius

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(Vector3D(radius, radius, radius))
