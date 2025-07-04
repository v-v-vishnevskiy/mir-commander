import logging
from typing import Self

from PySide6.QtGui import QMatrix4x4, QVector3D, QQuaternion

logger = logging.getLogger("OpenGL.Item")


class Item:
    def __init__(self):
        self.visible = True
        self.transform = QMatrix4x4()

        self.children: list[Self] = []
        self.parent: None | Self = None

        self._translation = QVector3D(0.0, 0.0, 0.0)
        self._rotation = QQuaternion()
        self._scale = QVector3D(1.0, 1.0, 1.0)

    def add_child(self, child: Self) -> bool:
        if not isinstance(child, Item):
            logger.error("Invalid child type: %s", child)
            return False

        if child.parent is not None:
            child.parent.remove_child(child)

        child.parent = self
        self.children.append(child)
        logger.debug("Added child: %s", child)
        return True

    def remove_child(self, child: Self) -> bool:
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            logger.debug("Removed child: %s", child)
            return True
        return False

    def clear_children(self):
        for child in self.children[:]:
            self.remove_child(child)

    def set_position(self, position: QVector3D):
        self._translation = position
        self._update_transform()

    def set_rotation(self, rotation: QQuaternion):
        self._rotation = rotation
        self._update_transform()

    def set_scale(self, scale: QVector3D):
        self._scale = scale
        self._update_transform()

    def translate(self, vector: QVector3D):
        self._translation += vector
        self._update_transform()

    def rotate(self, pitch: float, yaw: float, roll: float = 0.0):
        pitch_quat = QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), pitch)
        yaw_quat = QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), yaw)
        roll_quat = QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), roll)
        
        rotation = pitch_quat * yaw_quat * roll_quat
        self._rotation = rotation * self._rotation
        self._update_transform()

    def scale(self, factor: float):
        self._scale *= factor
        self._update_transform()

    def _update_transform(self):
        self.transform.setToIdentity()
        self.transform.translate(self._translation)
        self.transform.rotate(self._rotation)
        self.transform.scale(self._scale)

    def clear(self):
        self.clear_children()
        logger.debug("Cleared item: %s", self)

    def paint(self):
        if not self.visible:
            return

        self.paint_self()

        for child in self.children:
            child.paint()

    def paint_self(self):
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.__class__.__name__
