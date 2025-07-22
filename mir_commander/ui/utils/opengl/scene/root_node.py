from .base_node import BaseNode
from .rendering_container import RenderingContainer


class RootNode:
    __slots__ = ("_normal_containers", "_picking_container")

    def __init__(self):
        self._normal_containers: dict[str, RenderingContainer] = {
            "char": RenderingContainer("char"),
            "container": RenderingContainer("container"),
            "opaque": RenderingContainer("opaque"),
            "text": RenderingContainer("text"),
            "transparent": RenderingContainer("transparent"),
        }
        self._picking_container: RenderingContainer = RenderingContainer("picking")

    @property
    def containers(self) -> tuple[dict[str, RenderingContainer], RenderingContainer]:
        return self._normal_containers, self._picking_container

    def add_node(self, node: BaseNode):
        node.set_root_node(self)
        self.notify_add_node(node)

    def remove_node(self, node: BaseNode):
        node.set_root_node(None)
        self.notify_remove_node(node)

    def clear(self):
        for container in self._normal_containers.values():
            container.clear()
        self._picking_container.clear()

    def clear_transform_dirty(self):
        for container in self._normal_containers.values():
            container.clear_transform_dirty()
        self._picking_container.clear_transform_dirty()

    def notify_add_node(self, node: BaseNode):
        if node.visible is False:
            return

        self._normal_containers[node.node_type].add_node(node)

        if node.picking_visible:
            self._picking_container.add_node(node)

    def notify_remove_node(self, node: BaseNode):
        self._normal_containers[node.node_type].remove_node(node)

        if node.picking_visible:
            self._picking_container.remove_node(node)

    def notify_transform_changed(self, node: BaseNode):
        self._normal_containers[node.node_type].set_transform_dirty(node)

        if node.picking_visible:
            self._picking_container.set_transform_dirty(node)

    def notify_visible_changed(self, node: BaseNode):
        if node.visible:
            self.notify_add_node(node)
        else:
            self.notify_remove_node(node)

    def find_node_by_id(self, node_id: int) -> BaseNode | None:
        node = self._picking_container.find_node_by_id(node_id)
        if node is not None:
            return node
        return None

    def __repr__(self):
        return "RootNode()"
