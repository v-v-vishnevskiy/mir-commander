import logging
from typing import Self

from PySide6.QtGui import QMatrix4x4, QVector3D, QQuaternion

from ..utils import id_to_color

logger = logging.getLogger("OpenGL.Item")


class Item:
    _id_counter = 0

    def __init__(self, is_container: bool = False, visible: bool = True, picking_visible: bool = True, transparent: bool = False):
        Item._id_counter += 1
        self._id = Item._id_counter

        self._is_container = is_container
        self._visible = visible
        self._transparent = transparent

        self.picking_visible = picking_visible
        self.picking_color = id_to_color(self._id)

        self.children: list[Self] = []
        self.parent: None | Self = None

        self._update_transform_for_children = True

        self._parent_transform = QMatrix4x4()
        self._transform = QMatrix4x4()  # model matrix
        self._scale = QVector3D(1.0, 1.0, 1.0)
        self._rotation = QQuaternion()
        self._translation = QVector3D(0.0, 0.0, 0.0)
        self._transform_dirty = True

    def notify_parents_of_change(self):
        current = self.parent
        while current is not None:
            current.invalidate_cache()
            current = current.parent

    def invalidate_cache(self):
        pass

    @property
    def transform_dirty(self) -> bool:
        return self._transform_dirty

    def invalidate_transform(self):
        self._transform_dirty = True

    def validate_transform(self):
        self._transform_dirty = False

    @property
    def is_container(self) -> bool:
        return self._is_container

    def set_is_container(self, value: bool):
        self._is_container = value
        self.notify_parents_of_change()

    @property
    def transparent(self) -> bool:
        return self._transparent

    def set_transparent(self, value: bool):
        self._transparent = value
        self.notify_parents_of_change()

    @property
    def visible(self) -> bool:
        return self._visible

    def set_visible(self, value: bool):
        self._visible = value
        for child in self.children:
            child.set_visible(value)
        self.notify_parents_of_change()

    def toggle_visible(self):
        self._visible = not self._visible
        for child in self.children:
            child.toggle_visible()
        self.notify_parents_of_change()

    def update_parent_transform(self) -> QMatrix4x4:
        if self.parent is not None:
            self._parent_transform = self.parent.get_transform
            self.invalidate_transform()

        for child in self.children:
            child.update_parent_transform()

        self.notify_parents_of_change()

    @property
    def get_transform(self) -> QMatrix4x4:
        return self._parent_transform * self._transform

    def add_child(self, child: Self) -> bool:
        if not isinstance(child, Item):
            logger.error("Invalid child type: %s", child)
            return False

        if child.parent is not None:
            child.parent.remove_child(child)

        child.parent = self
        self.children.append(child)

        if self._update_transform_for_children:
            child.update_parent_transform()

        self.notify_parents_of_change()

        logger.debug("Added child: %s", child)
        return True

    def remove_child(self, child: Self) -> bool:
        if child in self.children:
            self.children.remove(child)
            child.parent = None

            self.notify_parents_of_change()

            logger.debug("Removed child: %s", child)
            return True
        return False

    def find_item_by_id(self, obj_id: int) -> Self | None:
        if self._id == obj_id:
            return self
        for child in self.children:
            item = child.find_item_by_id(obj_id)
            if item is not None:
                return item
        return None

    def set_translation(self, position: QVector3D):
        self._translation = position

        self._update_transform()

    def translate(self, vector: QVector3D):
        self._translation += vector

        self._update_transform()

    def set_rotation(self, rotation: QQuaternion):
        self._rotation = rotation

        self._update_transform()

    def rotate(self, pitch: float, yaw: float, roll: float = 0.0):
        pitch_quat = QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), pitch)
        yaw_quat = QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), yaw)
        roll_quat = QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), roll)

        rotation = pitch_quat * yaw_quat * roll_quat
        self._rotation = rotation * self._rotation

        self._update_transform()

    def set_scale(self, scale: QVector3D):
        self._scale = scale

        self._update_transform()

    def scale(self, factor: float):
        self._scale *= factor

        self._update_transform()

    def _update_transform(self):
        self._transform.setToIdentity()
        self._transform.rotate(self._rotation)
        self._transform.translate(self._translation)
        self._transform.scale(self._scale)

        self.invalidate_transform()

        if self._update_transform_for_children:
            for child in self.children:
                child.update_parent_transform()

        self.notify_parents_of_change()  # TODO: refactor this

    def clear(self):
        self.children.clear()

        self.notify_parents_of_change()

        logger.debug("Cleared item: %s", self)

    def get_all_items(self) -> list[Self]:
        items = [self]
        for child in self.children:
            items.extend(child.get_all_items())
        return items

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, is_container={self.is_container}, visible={self.visible}, transparent={self.transparent}, picking_visible={self.picking_visible})"
