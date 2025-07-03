import logging
from typing import Set

from OpenGL.GL import glMultMatrixf, glPopMatrix, glPushMatrix
from PySide6.QtGui import QMatrix4x4, QVector3D, QQuaternion

from .graphics_items.item import Item

logger = logging.getLogger("OpenGL.Scene")


class Scene:
    def __init__(self):
        self._items: Set[Item] = set()
        self._transform = QMatrix4x4()
        self._rotation = QQuaternion()
        self._scale = QVector3D(1.0, 1.0, 1.0)
        self._translation = QVector3D(0.0, 0.0, 0.0)

        self._update_transform()

    def add_item(self, item: Item) -> bool:
        if not isinstance(item, Item):
            logger.error("Invalid item type: %s", item)
            return False
        
        self._items.add(item)
        logger.debug("Added item to scene: %s", item)
        return True

    def remove_item(self, item: Item) -> bool:
        if item in self._items:
            self._items.remove(item)
            logger.debug("Removed item from scene: %s", item)
            return True
        return False

    def clear(self):
        for item in self._items:
            item.clear()
        self._items.clear()
        logger.debug("Scene cleared")

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

    def translate(self, x: float, y: float, z: float):
        self._translation += QVector3D(x, y, z)
        self._update_transform()

    def reset_transform(self):
        self._rotation = QQuaternion()
        self._scale = QVector3D(1.0, 1.0, 1.0)
        self._translation = QVector3D(0.0, 0.0, 0.0)
        self._update_transform()

    def _update_transform(self):
        self._transform = QMatrix4x4()

        self._transform.translate(self._translation)
        self._transform.rotate(self._rotation)
        self._transform.scale(self._scale)

    def paint(self):
        glPushMatrix()
        glMultMatrixf(self._transform.data())
        for item in self._items:
            if item.visible:
                item.paint()
        glPopMatrix()
