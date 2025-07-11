from .graphics_items.item import Item


class SceneGraph(Item):
    def __init__(self):
        super().__init__(is_container=True, picking_visible=False)

        self.add_item = self.add_child
        self.remove_item = self.remove_child

    def items(self) -> tuple[list[Item], list[Item]]:
        items = self.get_all_items()

        opaque_items = []
        transparent_items = []

        for item in items:
            if item.is_container or not item.visible:
                continue

            if item.transparent:
                transparent_items.append(item)
            else:
                opaque_items.append(item)

        return opaque_items, transparent_items

    def picking_items(self) -> list[Item]:
        result = []
        items = self.get_all_items()
        for item in items:
            if not item.is_container and item.visible and item.picking_visible:
                result.append(item)
        return result
