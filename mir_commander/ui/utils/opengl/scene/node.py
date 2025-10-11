from enum import Enum
from typing import TYPE_CHECKING, Any, Hashable, Optional, Self

from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D

from ..errors import NodeError, NodeNotFoundError, NodeParentError
from ..utils import Color4f, id_to_color
from .transform import Transform

if TYPE_CHECKING:
    from .root_node import RootNode

_ID_COUNTER_LIMIT = 255 * 255 * 255


class NodeType(Enum):
    CONTAINER = "container"
    OPAQUE = "opaque"
    TRANSPARENT = "transparent"
    TEXT = "text"
    CHAR = "char"


class Node:
    _id_counter = 0
    _picking_id_counter = 0

    __slots__ = (
        "_id",
        "_picking_id",
        "_root_node",
        "_parent",
        "_node_type",
        "_visible",
        "_transform_dirty",
        "_transform",
        "_transform_matrix",
        "_modify_children",
        "_picking_visible",
        "_picking_color",
        "_shader_name",
        "_texture_name",
        "_model_name",
        "_color",
        "_children",
        "metadata",
    )

    def __init__(
        self,
        node_type: NodeType,
        parent: Optional["Node"] = None,
        root_node: Optional["RootNode"] = None,
        visible: bool = True,
        picking_visible: bool = False,
    ):
        Node._id_counter += 1
        self._id = Node._id_counter

        self._node_type = node_type

        if root_node is None and parent is None:
            raise NodeError("Root node is required when parent is not provided")

        self._root_node: "RootNode" = root_node if root_node is not None else parent._root_node  # type: ignore[union-attr]

        self._parent = parent
        if parent is not None:
            parent._children.append(self)

        self._visible = visible
        self._picking_visible = picking_visible

        # True - transform has been changed, False - transform is up to date
        self._transform_dirty = True
        self._transform = Transform()
        self._transform_matrix = QMatrix4x4()

        self._modify_children: bool = False

        Node._picking_id_counter += 1
        if Node._picking_id_counter > _ID_COUNTER_LIMIT:
            Node._picking_id_counter = 1
        self._picking_id = Node._picking_id_counter

        self._picking_color = id_to_color(self._picking_id)

        self._shader_name: str = ""
        self._texture_name: str = ""
        self._model_name: str = ""
        self._color: Color4f = (1.0, 1.0, 1.0, 1.0)

        self._children: list[Self] = []
        self.metadata: dict[str, Any] = {}

    @property
    def id(self) -> int:
        return self._id

    @property
    def picking_id(self) -> int:
        return self._picking_id

    @property
    def parent(self) -> "Node":
        if self._parent is None:
            raise NodeParentError("Parent is not set")
        return self._parent

    @property
    def node_type(self) -> NodeType:
        return self._node_type

    @property
    def visible(self) -> bool:
        if self._parent is not None:
            return self._visible and self._parent.visible
        return self._visible

    @property
    def picking_visible(self) -> bool:
        return self._picking_visible

    @property
    def picking_color(self) -> Color4f:
        return self._picking_color

    @property
    def transform(self) -> QMatrix4x4:
        if self._transform_dirty:
            self._update_transform()
            self._transform_dirty = False
        return self._transform_matrix

    @property
    def shader_name(self) -> str:
        return self._shader_name

    @property
    def texture_name(self) -> str:
        return self._texture_name

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def color(self) -> Color4f:
        return self._color

    @property
    def group_id(self) -> Hashable:
        if self._node_type in (NodeType.OPAQUE, NodeType.TRANSPARENT, NodeType.CHAR):
            return self._shader_name, self._texture_name, self._model_name
        return None

    @property
    def children(self) -> list[Self]:
        return self._children

    def _get_all_children(self, include_self: bool = True) -> list[Self]:
        result = []
        if include_self:
            result.append(self)

        stack = self._children.copy()
        while stack:
            node = stack.pop()
            result.append(node)
            stack.extend(node._children)

        return result

    def get_node_by_id(self, node_id: int) -> Self:
        if self._id == node_id:
            return self
        for child in self._children:
            try:
                return child.get_node_by_id(node_id)
            except NodeNotFoundError:
                pass
        raise NodeNotFoundError()

    def _update_transform(self):
        if self._parent:
            self._transform_matrix = self._parent.transform * self._transform.matrix
        else:
            self._transform_matrix = self._transform.matrix

    def remove(self):
        if self._parent is not None:
            self._parent._children.remove(self)
            self._parent = None

        self.clear()
        self._root_node.notify_remove_node(self)

    def clear(self):
        root_node = self._root_node
        for node in self._get_all_children(include_self=False):
            if root_node is not None:
                root_node.notify_remove_node(node)
        self._children.clear()

    def set_visible(self, value: bool, apply_to_parents: bool = False, apply_to_children: bool = False):
        fn = self._root_node.notify_add_node if value else self._root_node.notify_remove_node

        if self._visible != value:
            self._visible = value
            fn(self)

        if apply_to_parents:
            parent = self._parent
            while parent is not None:
                if parent._visible != value:
                    parent._visible = value
                    fn(parent)
                parent = parent._parent

        for node in self._get_all_children(include_self=False):
            if apply_to_children:
                node.set_visible(value, False, True)
            else:
                if self._modify_children:
                    node._visible = value
                fn(node)

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

    def set_node_type(self, node_type: NodeType):
        if self._node_type == node_type:
            return

        self._root_node.notify_remove_node(self)
        self._node_type = node_type
        self._root_node.notify_add_node(self)

    def set_shader(self, shader_name: str):
        if self._shader_name == shader_name:
            return

        self._root_node.notify_remove_node(self)
        self._shader_name = shader_name
        self._root_node.notify_add_node(self)

    def set_texture(self, texture_name: str):
        if self._texture_name == texture_name:
            return

        self._root_node.notify_remove_node(self)
        self._texture_name = texture_name
        self._root_node.notify_add_node(self)

    def set_model(self, model_name: str):
        if self._model_name == model_name:
            return

        self._root_node.notify_remove_node(self)
        self._model_name = model_name
        self._root_node.notify_add_node(self)

    def set_color(self, color: Color4f):
        if self._color == color:
            return

        self._color = color
        self._root_node.notify_set_dirty(self)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._id}, visible={self.visible})"
