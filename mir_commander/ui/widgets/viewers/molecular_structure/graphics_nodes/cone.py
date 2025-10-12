from PySide6.QtGui import QQuaternion, QVector3D

from ..consts import VAO_CONE_RESOURCE_NAME
from .base import BaseGraphicsNode


class Cone(BaseGraphicsNode):
    def __init__(self, direction: QVector3D, radius: float, length: float, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = radius
        self._length = length
        self.set_model(VAO_CONE_RESOURCE_NAME)
        self.set_rotation(QQuaternion.rotationTo(QVector3D(0.0, 0.0, -1.0), direction))
        self.set_scale(QVector3D(radius, radius, length))

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(QVector3D(radius, radius, self._length))

    def set_length(self, length: float):
        self._length = length
        self.set_scale(QVector3D(self._radius, self._radius, length))
