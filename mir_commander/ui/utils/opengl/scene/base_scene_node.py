from typing import Hashable, Self

from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D

from .base_node import BaseNode
from .transform import Transform


class BaseSceneNode(BaseNode):
    __slots__ = ("_transform_dirty", "_transform", "_transform_matrix", "_modify_children")

    def __init__(self, parent: Self, visible: bool):
        self._visible = visible

        # True - transform has been changed, False - transform is up to date
        self._transform_dirty = True
        self._transform = Transform()
        self._transform_matrix = QMatrix4x4()

        self._modify_children: bool = False

        super().__init__(parent)

    @property
    def group_id(self) -> Hashable:
        return None

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def transform(self) -> QMatrix4x4:
        if self._transform_dirty:
            self._update_transform()
            self._transform_dirty = False
        return self._transform_matrix

    def set_visible(self, value: bool):
        if self._visible == value:
            return

        self._visible = value

        fn = self._root_node.notify_add_node if value else self._root_node.notify_remove_node

        for node in self._get_all_children(include_self=True):
            if self._modify_children:
                node._visible = value
            fn(node)

    def _update_transform(self):
        if self.parent:
            self._transform_matrix = self.parent.transform * self._transform.matrix
        else:
            self._transform_matrix = self._transform.matrix

    def invalidate_transform(self):
        root_node = self._root_node
        for node in self._get_all_children(include_self=True):
            node._transform_dirty = True
            if root_node is not None:
                root_node.notify_set_dirty(node)

    def scale(self, value: QVector3D):
        self._transform.scale(value)
        self.invalidate_transform()

    def set_scale(self, value: QVector3D):
        self._transform.set_scale(value)
        self.invalidate_transform()

    def rotate(self, pitch: float, yaw: float, roll: float = 0.0):
        self._transform.rotate(pitch, yaw, roll)
        self.invalidate_transform()

    def set_rotation(self, value: QQuaternion):
        self._transform.set_rotation(value)
        self.invalidate_transform()

    def translate(self, translation: QVector3D):
        self._transform.translate(translation)
        self.invalidate_transform()

    def set_translation(self, translation: QVector3D):
        self._transform.set_translation(translation)
        self.invalidate_transform()
