from .graphics_items.item import Item


class Scene(Item):
    def __init__(self):
        super().__init__()

        self.add_item = self.add_child
        self.remove_item = self.remove_child

    def paint_self(self):
        pass
