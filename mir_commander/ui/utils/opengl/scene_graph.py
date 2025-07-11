from .graphics_items.item import Item


class SceneGraph(Item):
    def __init__(self):
        super().__init__(is_container=True, picking_visible=False)

        self.add_item = self.add_child
        self.remove_item = self.remove_child
