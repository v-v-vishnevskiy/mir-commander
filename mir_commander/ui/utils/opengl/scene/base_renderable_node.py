from typing import Hashable

from mir_commander.ui.utils.opengl.utils import Color4f

from ..utils import id_to_color
from .base_node import BaseNode
from .base_scene_node import BaseSceneNode


class BaseRenderableNode(BaseSceneNode):
    _id_counter = 0

    __slots__ = ("_id", "_picking_visible", "picking_color", "_shader_name", "_texture_name", "_model_name", "_color")

    def __init__(self, parent: BaseNode, visible: bool = True, picking_visible: bool = True):
        super().__init__(parent, visible)

        BaseRenderableNode._id_counter += 1
        self._id = BaseRenderableNode._id_counter

        self._picking_visible = picking_visible
        self.picking_color = id_to_color(self._id)

        self._shader_name: str = ""
        self._texture_name: str = ""
        self._model_name: str = ""
        self._color: Color4f = (1.0, 1.0, 1.0, 1.0)

    @property
    def id(self) -> int:
        return self._id

    @property
    def group_id(self) -> Hashable:
        return self._shader_name, self._texture_name, self._model_name

    @property
    def picking_visible(self) -> bool:
        return self._picking_visible

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
        return (
            f"{self.__class__.__name__}("
            f"id={self._id}, "
            f"visible={self.visible}, "
            f"picking_visible={self._picking_visible}, "
            f"shader='{self._shader_name}', "
            f"texture='{self._texture_name}', "
            f"model='{self._model_name}', "
            f"color={self._color}"
            ")"
        )
