from .base import Resource
from .rendering_container import RenderingContainer
from .root_scene_node import RootSceneNode
from .scene_node import SceneNode
from .transform import Transform


class Scene(Resource):
    __slots__ = ("_containers", "_root_node", "transform")

    def __init__(self, name: str):
        super().__init__(name)

        self._containers = (
            RenderingContainer("opaque"),
            RenderingContainer("transparent"),
            RenderingContainer("text"),
            RenderingContainer("picking"),
        )
        self._root_node = RootSceneNode(*self._containers)

        self.transform = Transform()

    @property
    def root_node(self) -> RootSceneNode:
        return self._root_node

    def add_node(self, node: SceneNode):
        self._root_node.add_node(node)

    def remove_node(self, node: SceneNode):
        self._root_node.remove_node(node)

    def find_node_by_id(self, node_id: int) -> SceneNode | None:
        if node_id == 0:
            return None

        return self._root_node.find_node_by_id(node_id)

    def clear(self):
        self._root_node.clear()

    def containers(self) -> tuple[RenderingContainer, RenderingContainer, RenderingContainer, RenderingContainer]:
        return self._containers

    def __repr__(self):
        return f"Scene(name={self.name}, root_node={self._root_node})"
