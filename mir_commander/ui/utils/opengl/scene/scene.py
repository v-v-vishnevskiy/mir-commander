from mir_commander.ui.utils.opengl.resource_manager.base import Resource

from .base_node import BaseNode
from .rendering_container import RenderingContainer
from .root_node import RootNode
from .transform import Transform


class Scene(Resource):
    __slots__ = ("_root_node", "transform")

    def __init__(self, name: str):
        super().__init__(name)

        self._root_node = RootNode()

        self.transform = Transform()

    @property
    def root_node(self) -> RootNode:
        return self._root_node

    @property
    def containers(self) -> tuple[dict[str, RenderingContainer], RenderingContainer]:
        return self._root_node.containers

    def find_node_by_id(self, node_id: int) -> BaseNode:
        return self._root_node.find_node_by_id(node_id)

    def clear(self):
        self._root_node.clear()

    def __repr__(self):
        return f"Scene(name={self.name}, root_node={self._root_node})"
