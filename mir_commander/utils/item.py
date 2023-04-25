from typing import Any, List, Union


class Item:
    def __init__(self, title: str, data: Any = None):
        self.title = title
        self.data = data
        self._items: List["Item"] = []

    def append(self, item: "Item"):
        self._items.append(item)

    def insert(self, index: int, item: "Item"):
        self._items.insert(index, item)

    def get(self, index: int) -> Union[None, "Item"]:
        try:
            return self._items[index]
        except IndexError:
            return None

    def get_nested(self, indices: List[int]) -> Union[None, "Item"]:
        item = self.get(indices[0])
        if len(indices) > 1:
            if isinstance(item, self.__class__):
                return item.get_nested(indices[1:])
            else:
                return None
        else:
            return item

    def pop(self, index: int = -1) -> Union[None, "Item"]:
        try:
            return self._items.pop(index)
        except IndexError:
            return None

    def pop_nested(self, indices: List[int]) -> Union[None, "Item"]:
        if not indices:
            return None
        elif len(indices) == 1:
            return self.pop(indices[0])
        else:
            item = self.get(indices[0])
            if isinstance(item, self.__class__):
                return item.pop_nested(indices[1:])
            else:
                return None
