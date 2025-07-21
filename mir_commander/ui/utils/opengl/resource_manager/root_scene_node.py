from .rendering_container import RenderingContainer
from .scene_node import SceneNode


class RootSceneNode:
    def __init__(
        self,
        opaque_rendering_container: RenderingContainer,
        transparent_rendering_container: RenderingContainer,
        text_rendering_container: RenderingContainer,
        picking_rendering_container: RenderingContainer,
    ):
        self._nodes: list[SceneNode] = []
        self._opaque_rendering_container: RenderingContainer = opaque_rendering_container
        self._transparent_rendering_container: RenderingContainer = transparent_rendering_container
        self._text_rendering_container: RenderingContainer = text_rendering_container
        self._picking_rendering_container: RenderingContainer = picking_rendering_container

    def add_node(self, node: SceneNode):
        node.set_root_node(self)
        self._nodes.append(node)
        self.notify_add_node(node)

    def remove_node(self, node: SceneNode):
        node.set_root_node(None)
        self._nodes.remove(node)
        self.notify_remove_node(node)

    def clear(self):
        self._nodes.clear()
        self._opaque_rendering_container.clear()
        self._transparent_rendering_container.clear()
        self._picking_rendering_container.clear()

    def clear_transform_dirty(self):
        self._opaque_rendering_container.clear_transform_dirty()
        self._transparent_rendering_container.clear_transform_dirty()
        self._text_rendering_container.clear_transform_dirty()
        self._picking_rendering_container.clear_transform_dirty()

    def notify_add_node(self, node: SceneNode):
        if node.is_container is True or node.visible is False:
            return

        if node.is_text is True:
            self._text_rendering_container.add_node(node)
            return

        if node.transparent:
            self._transparent_rendering_container.add_node(node)
        else:
            self._opaque_rendering_container.add_node(node)

        if node.picking_visible:
            self._picking_rendering_container.add_node(node)

    def notify_remove_node(self, node: SceneNode):
        if node.is_container is True:
            return

        if node.is_text is True:
            self._text_rendering_container.remove_node(node)
            return

        if node.transparent:
            self._transparent_rendering_container.remove_node(node)
        else:
            self._opaque_rendering_container.remove_node(node)

        if node.picking_visible:
            self._picking_rendering_container.remove_node(node)

    def notify_transform_changed(self, node: SceneNode):
        if node.is_container is True:
            return

        if node.is_text is True:
            self._text_rendering_container.set_transform_dirty(node)
            return

        if node.transparent:
            self._transparent_rendering_container.set_transform_dirty(node)
        else:
            self._opaque_rendering_container.set_transform_dirty(node)

        if node.picking_visible:
            self._picking_rendering_container.set_transform_dirty(node)

    def notify_visible_changed(self, node: SceneNode):
        if node.is_container is True:
            return

        if node.visible:
            self.notify_add_node(node)
        else:
            self.notify_remove_node(node)

    def find_node_by_id(self, node_id: int) -> SceneNode | None:
        for node in self._nodes:
            node = node.find_node_by_id(node_id)
            if node is not None:
                return node
        return None

    def __repr__(self):
        return f"RootSceneNode(nodes={self._nodes})"
