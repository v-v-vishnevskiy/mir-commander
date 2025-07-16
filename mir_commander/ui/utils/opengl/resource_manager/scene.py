from .base import Resource
from .scene_node import SceneNode
from .transform import Transform


class Scene(Resource):
    __slots__ = ("_root_node", "_opaque_nodes", "_transparent_nodes", "_picking_nodes", "transform")

    def __init__(self, name: str):
        super().__init__(name)

        self._root_node: SceneNode = SceneNode(is_container=True)

        self._opaque_nodes: list[SceneNode] = []
        self._transparent_nodes: list[SceneNode] = []
        self._picking_nodes: list[SceneNode] = []

        self.transform = Transform()

    @property
    def root_node(self) -> SceneNode:
        return self._root_node

    def add_node(self, node: SceneNode):
        self._root_node.add_node(node)

    def remove_node(self, node: SceneNode):
        self._root_node.remove_node(node)

    def find_node_by_id(self, obj_id: int) -> SceneNode | None:
        return self._root_node.find_node_by_id(obj_id)

    def clear(self):
        self._root_node.clear()

    def nodes(self) -> tuple[list[SceneNode], list[SceneNode], list[SceneNode]]:
        if self._root_node.nodes_dirty:
            self._update_cache()

        return self._opaque_nodes, self._transparent_nodes, self._picking_nodes

    def _update_cache(self):
        nodes = self._root_node.get_all_nodes()

        self._opaque_nodes = []
        self._transparent_nodes = []
        self._picking_nodes = []

        for node in nodes:
            if node.is_container or not node.visible:
                continue

            if node.transparent:
                self._transparent_nodes.append(node)
            else:
                self._opaque_nodes.append(node)

            if node.picking_visible:
                self._picking_nodes.append(node)

    def __repr__(self):
        return f"Scene(name={self.name}, root_node={self._root_node})"
