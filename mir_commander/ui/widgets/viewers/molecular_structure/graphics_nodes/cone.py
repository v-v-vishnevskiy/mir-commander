from PySide6.QtGui import QQuaternion, QVector3D

from ..consts import VAO_CONE_RESOURCE_NAME
from .base import BaseGraphicsNode


class Cone(BaseGraphicsNode):
    def __init__(self, direction: QVector3D, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._radius = 1.0
        self._length = 1.0
        self.set_model(VAO_CONE_RESOURCE_NAME)
        self.set_rotation(QQuaternion.rotationTo(QVector3D(0.0, 0.0, 1.0), direction))
        self.set_scale(QVector3D(self._radius, self._radius, self._length))

    def set_size(self, radius: float, length: float):
        self._radius = radius
        self._length = length
        self.set_scale(QVector3D(radius, radius, length))
