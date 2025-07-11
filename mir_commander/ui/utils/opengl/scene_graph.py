from .graphics_items.item import Item


class SceneGraph(Item):
    def __init__(self):
        super().__init__(is_container=True, picking_visible=False)

        self.add_item = self.add_child
        self.remove_item = self.remove_child

        self._opaque_items: list[Item] = []
        self._transparent_items: list[Item] = []
        self._picking_items: list[Item] = []

        self._cache_dirty = True

    def invalidate_cache(self):
        self._cache_dirty = True

    def items(self) -> tuple[list[Item], list[Item], list[Item]]:
        if self._cache_dirty:
            self._update_cache()

        return self._opaque_items, self._transparent_items, self._picking_items

    def _update_cache(self):
        items = self.get_all_items()

        self._opaque_items = []
        self._transparent_items = []
        self._picking_items = []

        for item in items:
            if item.is_container or not item.visible:
                continue

            if item.transparent:
                self._transparent_items.append(item)
            else:
                self._opaque_items.append(item)
            
            if item.picking_visible:
                self._picking_items.append(item)

        self._cache_dirty = False
