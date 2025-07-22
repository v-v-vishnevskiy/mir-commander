from typing import Hashable

from .base_node import BaseNode


class RenderingContainer:
    def __init__(self, name: str):
        self.name = name
        self._batches: dict[Hashable, list[BaseNode]] = {}
        self.transform_dirty: dict[tuple, bool] = {}

    def __bool__(self):
        return bool(self._batches)

    @property
    def batches(self) -> list[Hashable, list[BaseNode]]:
        return sorted(((group_id, nodes) for group_id, nodes in self._batches.items()))

    def add_node(self, node: BaseNode):
        group_id = node.group_id

        if group_id not in self._batches:
            self._batches[group_id] = []

        if node not in self._batches[group_id]:
            self.transform_dirty[group_id] = True
            self._batches[group_id].append(node)

    def remove_node(self, node: BaseNode):
        group_id = node.group_id

        try:
            self._batches[group_id].remove(node)
            self.transform_dirty[group_id] = True

            if not self._batches[group_id]:
                del self._batches[group_id]
        except (KeyError, ValueError):
            # Node was already removed
            pass

    def set_transform_dirty(self, node: BaseNode):
        self.transform_dirty[node.group_id] = True

    def clear(self):
        self._batches.clear()
        self.transform_dirty.clear()

    def clear_transform_dirty(self):
        self.transform_dirty.clear()

    def find_node_by_id(self, node_id: int) -> BaseNode | None:
        for nodes in self._batches.values():
            for node in nodes:
                if node._id == node_id:
                    return node
        return None

    def __repr__(self) -> str:
        _batches = []
        for group_id, batches in self.batches:
            _batches.append(f"group_id={group_id}:")
            for node in batches:
                _batches.append(f"  {node}")

        batches = "\n".join(_batches)

        return f"{self.__class__.__name__}(name={self.name}, batches={batches})"
