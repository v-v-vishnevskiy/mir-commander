from .base_node import BaseNode
from .base_scene_node import BaseSceneNode
from .rendering_container import RenderingContainer


class RootNode(BaseNode):
    node_type = "root"

    __slots__ = ("_normal_containers", "_text_container", "_picking_container")

    def __init__(self):
        super().__init__(parent=None)

        self._normal_containers: dict[str, RenderingContainer] = {
            "char": RenderingContainer("char"),
            "opaque": RenderingContainer("opaque"),
            "transparent": RenderingContainer("transparent"),
        }
        self._text_container: RenderingContainer = RenderingContainer("text")
        self._picking_container: RenderingContainer = RenderingContainer("picking")

    @property
    def containers(self) -> tuple[dict[str, RenderingContainer], RenderingContainer, RenderingContainer]:
        return self._normal_containers, self._text_container, self._picking_container

    def clear(self):
        for container in self._normal_containers.values():
            container.clear()
        self._text_container.clear()
        self._picking_container.clear()

    def clear_dirty(self):
        for container in self._normal_containers.values():
            container.clear_dirty()
        self._text_container.clear_dirty()
        self._picking_container.clear_dirty()

    def notify_add_node(self, node: BaseSceneNode):
        if node.node_type is None or node.visible is False:
            return

        if node.node_type == "text":
            self._text_container.add_node(node)
        else:
            self._normal_containers[node.node_type].add_node(node)
            if node.picking_visible:
                self._picking_container.add_node(node)

    def notify_remove_node(self, node: BaseSceneNode):
        if node.node_type is None:
            return

        if node.node_type == "text":
            self._text_container.remove_node(node)
        else:
            self._normal_containers[node.node_type].remove_node(node)
            if node.picking_visible:
                self._picking_container.remove_node(node)

    def notify_set_dirty(self, node: BaseSceneNode):
        if node.node_type is None:
            return

        if node.node_type == "text":
            self._text_container.set_dirty(node)
        else:
            self._normal_containers[node.node_type].set_dirty(node)
            if node.picking_visible:
                self._picking_container.set_dirty(node)

    def find_node_by_id(self, node_id: int) -> BaseSceneNode:
        return self._picking_container.find_node_by_id(node_id)

    def __repr__(self):
        return "RootNode()"
