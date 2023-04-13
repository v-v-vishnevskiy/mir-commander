from typing import Any, List, Union


class ItemsModel:
    def __init__(self, title: str):
        self.title = title
        self._items: List[Union[Any, "ItemsModel"]] = []

    def append(self, item: Union[Any, "ItemsModel"]):
        self._items.append(item)

    def insert(self, index: int, item: Union[Any, "ItemsModel"]):
        self._items.insert(index, item)

    def get(self, index: int) -> Union[None, Any, "ItemsModel"]:
        try:
            return self._items[index]
        except IndexError:
            return None

    def get_nested(self, indices: List[int]) -> Union[None, Any, "ItemsModel"]:
        item = self.get(indices[0])
        if len(indices) > 1:
            if isinstance(item, self.__class__):
                return item.get_nested(indices[1:])
            else:
                return None
        else:
            return item

    def pop(self, index: int = -1) -> Union[None, Any, "ItemsModel"]:
        try:
            return self._items.pop(index)
        except IndexError:
            return None

    def pop_nested(self, indices: List[int]) -> Union[None, Any, "ItemsModel"]:
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
