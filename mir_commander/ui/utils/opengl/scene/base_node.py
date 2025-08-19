from typing import Self


class BaseNode:
    node_type: None | str = None

    __slots__ = ("_root_node", "parent", "_children")

    def __init__(self, parent: None | Self):
        self._root_node: None | Self = None
        if parent is not None:
            self._root_node = parent if parent.node_type == "root" else parent._root_node

        self.parent: None | Self = None
        if parent is not None and parent.node_type != "root":
            self.parent = parent
            parent._children.append(self)

        self._children: list[Self] = []

    @property
    def children(self) -> list[Self]:
        return self._children

    def _get_all_children(self, include_self: bool = True) -> list[Self]:
        result = []
        if include_self:
            result.append(self)

        stack = self._children.copy()
        while stack:
            node = stack.pop()
            result.append(node)
            stack.extend(node._children)

        return result

    def remove(self):
        if self.parent is not None:
            self.parent._children.remove(self)
            self.parent = None

        self.clear()
        self._root_node.notify_remove_node(self)

    def clear(self):
        root_node = self._root_node
        for node in self._get_all_children(include_self=False):
            if root_node is not None:
                root_node.notify_remove_node(node)
        self._children.clear()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(parent={self.parent}, root_node={self._root_node}, children={self._children})"
        )
