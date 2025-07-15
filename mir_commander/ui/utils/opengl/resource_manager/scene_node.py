from typing import Self

from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D

from mir_commander.ui.utils.opengl.utils import Color4f

from ..utils import id_to_color

from .transform import Transform


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

        self._is_container = is_container
        self._visible = visible
        self._transparent = transparent
        self._picking_visible = picking_visible

        self.picking_color = id_to_color(self._id)

        # 1 - transform has been changed, 0 - transform is up to date
        self._transform_dirty = 1
        self._transform = Transform()
        self._transform_matrix = QMatrix4x4()

        # True - nodes have been added or removed, False - nodes are up to date
        self._nodes_dirty = False
        self._nodes: list[Self] = []

        self.parent: None | Self = None

        self._color: Color4f = (0.5, 0.5, 0.5, 1.0)
        self._mesh_name: str = ""
        self._vbo_name: str = ""
        self._shader_name: str = ""

    @property
    def is_container(self) -> bool:
        return self._is_container

    @property
    def visible(self) -> bool:
        return self._visible

    def set_visible(self, value: bool):
        self._visible = value
        for node in self._nodes:
            node.set_visible(value)
        self.invalidate_root_node()

    @property
    def transparent(self) -> bool:
        return self._transparent

    @property
    def picking_visible(self) -> bool:
        return self._picking_visible

    @property
    def transform(self) -> QMatrix4x4:
        if self._transform_dirty:
            self._update_transform()
            self._transform_dirty = 0
        return self._transform_matrix

    @property
    def transform_dirty(self) -> int:
        return self._transform_dirty

    @property
    def nodes_dirty(self) -> bool:
        return self._nodes_dirty

    @property
    def color(self) -> Color4f:
        return self._color

    @property
    def mesh(self) -> str:
        return self._mesh_name

    @property
    def vbo(self) -> str:
        return self._vbo_name

    @property
    def shader(self) -> str:
        return self._shader_name

    def _update_transform(self):
        if self.parent:
            self._transform_matrix = self.parent.transform * self._transform.matrix
        else:
            self._transform_matrix = self._transform.matrix

    def invalidate_transform(self):
        self._transform_dirty = 1
        for node in self._nodes:
            node.invalidate_transform()

    def invalidate_root_node(self):
        root_node = self
        parent = self.parent
        while parent is not None:
            root_node = parent
            parent = parent.parent
        root_node._nodes_dirty = True

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

    def add_node(self, node: Self):
        self._nodes.append(node)
        node.parent = self
        self.invalidate_root_node()

    def remove_node(self, node: Self):
        self._nodes.remove(node)
        node.parent = None
        self.invalidate_root_node()

    def clear(self):
        self._nodes.clear()
        self.invalidate_root_node()

    def find_node_by_id(self, obj_id: int) -> Self | None:
        if obj_id == 0:
            return None

        if self._id == obj_id:
            return self

        # TODO: optimize this
        for node in self._nodes:
            node = node.find_node_by_id(obj_id)
            if node is not None:
                return node
        return None

    def get_all_nodes(self) -> list[Self]:
        result = [self]
        for node in self._nodes:
            result.extend(node.get_all_nodes())

        self._nodes_dirty = False

        return result

    def set_color(self, color: Color4f):
        self._color = color

    def set_mesh(self, mesh_name: str):
        self._mesh_name = mesh_name

    def set_vbo(self, vbo_name: str):
        self._vbo_name = vbo_name

    def set_shader(self, shader_name: str):
        self._shader_name = shader_name

    def __repr__(self):
        return f"{self.__class__.__name__}(" \
            f"id={self._id}, " \
            f"color={self._color}, " \
            f"mesh={self._mesh_name}, " \
            f"vbo={self._vbo_name}, " \
            f"shader={self._shader_name}, " \
            f"nodes_dirty={self._nodes_dirty}" \
            ")"
