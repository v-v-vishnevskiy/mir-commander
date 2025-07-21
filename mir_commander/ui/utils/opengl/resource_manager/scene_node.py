from typing import Self, TYPE_CHECKING, Optional

from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D

from mir_commander.ui.utils.opengl.utils import Color4f

from ..utils import id_to_color

from .transform import Transform

if TYPE_CHECKING:
    from .root_scene_node import RootSceneNode


class SceneNode:
    _id_counter = 0

    def __init__(
        self,
        is_container: bool = False,
        visible: bool = True,
        transparent: bool = False,
        picking_visible: bool = False,
    ):
        SceneNode._id_counter += 1
        self._id = SceneNode._id_counter

        self._root_node: Optional["RootSceneNode"] = None

        self._is_container = is_container
        self._visible = visible
        self._transparent = transparent
        self._picking_visible = picking_visible
        self._is_text = False

        self.picking_color = id_to_color(self._id)

        # True - transform has been changed, False - transform is up to date
        self._transform_dirty = True
        self._transform = Transform()
        self._transform_matrix = QMatrix4x4()

        self._nodes: list[Self] = []

        self.parent: None | Self = None

        self._shader_name: None | str = None
        self._model_name: None | str = None
        self._color: Color4f = (1.0, 1.0, 1.0, 1.0)
        self._texture_name: None | str = None

        self.center = QVector3D(0.0, 0.0, 0.0)

    @property
    def group_id(self) -> tuple[str, str, str]:
        return self._shader_name, self._texture_name, self._model_name

    @property
    def is_container(self) -> bool:
        return self._is_container

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def transparent(self) -> bool:
        return self._transparent

    @property
    def picking_visible(self) -> bool:
        return self._picking_visible

    @property
    def is_text(self) -> bool:
        return self._is_text

    @property
    def transform(self) -> QMatrix4x4:
        if self._transform_dirty:
            self._update_transform()
            self._transform_dirty = False
        return self._transform_matrix

    @property
    def nodes(self) -> list[Self]:
        return self._nodes

    @property
    def shader_name(self) -> None | str:
        return self._shader_name

    @property
    def model_name(self) -> None | str:
        return self._model_name

    @property
    def color(self) -> Color4f:
        return self._color

    @property
    def texture_name(self) -> None | str:
        return self._texture_name

    def _update_transform(self):
        if self.parent:
            self._transform_matrix = self.parent.transform * self._transform.matrix
        else:
            self._transform_matrix = self._transform.matrix

    def _get_children(self, include_self: bool = True) -> list[Self]:
        result = []
        if include_self:
            result.append(self)

        stack = self._nodes.copy()
        while stack:
            node = stack.pop()
            result.append(node)
            stack.extend(node.nodes)

        return result

    def notify_visible_changed(self):
        root_node = self._root_node
        for node in self._get_children(include_self=True):
            if root_node is not None:
                root_node.notify_visible_changed(node)

    def set_visible(self, value: bool):
        if self._visible == value:
            return

        root_node = self._root_node
        for node in self._get_children(include_self=True):
            if node._visible != value:
                node._visible = value
                if root_node is not None:
                    root_node.notify_visible_changed(node)

    def add_node(self, node: Self):
        if node in self._nodes:
            return

        node.parent = self
        if self._root_node is not None:
            node.set_root_node(self._root_node)
        self._nodes.append(node)
        node.invalidate_transform()
        if self._root_node is not None:
            self._root_node.notify_add_node(node)

    def remove_node(self, node: Self):
        if node not in self._nodes:
            return

        self._nodes.remove(node)
        node.parent = None
        if self._root_node is not None:
            self._root_node.notify_remove_node(node)

    def clear(self):
        root_node = self._root_node
        for node in self._get_children(include_self=False):
            if root_node is not None:
                root_node.notify_remove_node(node)
        self._nodes.clear()

    def set_root_node(self, root_node: "RootSceneNode"):
        if self._root_node is not None and id(self._root_node) != id(root_node):
            self.remove_root_node()

        for node in self._get_children(include_self=True):
            root_node.notify_add_node(node)
            node._root_node = root_node
        
        self._root_node = root_node

    def remove_root_node(self):
        root_node = self._root_node

        if root_node is None:
            return

        for node in self._get_children(include_self=True):
            root_node.notify_remove_node(node)
            node._root_node = None

    def invalidate_transform(self):
        root_node = self._root_node
        for node in self._get_children(include_self=True):
            node._transform_dirty = True
            if root_node is not None:
                root_node.notify_transform_changed(node)

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

    def find_node_by_id(self, node_id: int) -> Self | None:
        if self._id == node_id:
            return self

        for node in self._nodes:
            node = node.find_node_by_id(node_id)
            if node is not None:
                return node
        return None

    def set_shader(self, shader_name: str):
        self._shader_name = shader_name

    def set_model(self, model_name: str):
        self._model_name = model_name

    def set_color(self, color: Color4f):
        self._color = color

    def set_texture(self, texture_name: str):
        self._texture_name = texture_name

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
            f"id={self._id}, " \
            f"visible={self._visible}, " \
            f"transparent={self._transparent}, " \
            f"picking_visible={self._picking_visible}, " \
            f"shader='{self._shader_name}', " \
            f"model='{self._model_name}', " \
            f"color={self._color}, " \
            f"texture='{self._texture_name}'" \
            ")"
