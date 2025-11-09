from typing import cast

from .node import Node, NodeType
from .rendering_container import RenderingContainer
from .text_node import TextNode


class RootNode:
    __slots__ = ("_normal_containers", "_text_container", "_picking_container")

    def __init__(self):
        self._normal_containers: dict[NodeType, RenderingContainer[Node]] = {
            NodeType.CHAR: RenderingContainer("char"),
            NodeType.OPAQUE: RenderingContainer("opaque"),
            NodeType.TRANSPARENT: RenderingContainer("transparent"),
        }
        self._text_container: RenderingContainer[TextNode] = RenderingContainer("text")
        self._picking_container: RenderingContainer[Node] = RenderingContainer("picking")

    @property
    def containers(
        self,
    ) -> tuple[dict[NodeType, RenderingContainer[Node]], RenderingContainer[TextNode], RenderingContainer[Node]]:
        return self._normal_containers, self._text_container, self._picking_container

    def clear(self):
        for container in self._normal_containers.values():
            container.clear()
        self._text_container.clear()
        self._picking_container.clear()

    def notify_add_node(self, node: Node):
        if node.node_type == NodeType.CONTAINER or node.visible is False:
            return

        if node.node_type == NodeType.TEXT:
            self._text_container.add_node(cast(TextNode, node))
        else:
            self._normal_containers[node.node_type].add_node(node)
            if node.picking_visible:
                self._picking_container.add_node(node)

    def notify_remove_node(self, node: Node):
        if node.node_type == NodeType.CONTAINER:
            return

        if node.node_type == NodeType.TEXT:
            self._text_container.remove_node(cast(TextNode, node))
        else:
            self._normal_containers[node.node_type].remove_node(node)
            if node.picking_visible:
                self._picking_container.remove_node(node)

    def notify_set_dirty(self, node: Node):
        if node.node_type == NodeType.CONTAINER:
            return

        if node.node_type == NodeType.TEXT:
            self._text_container.set_dirty(cast(TextNode, node))
        else:
            self._normal_containers[node.node_type].set_dirty(node)
            if node.picking_visible:
                self._picking_container.set_dirty(node)

    def find_node_by_picking_id(self, picking_id: int) -> Node:
        return self._picking_container.find_node_by_picking_id(picking_id)

    def __repr__(self):
        return "RootNode()"
