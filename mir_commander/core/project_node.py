from typing import Any, Iterable, Self, SupportsIndex

from pydantic import ConfigDict, PrivateAttr, field_validator

from mir_commander.plugin_system.project_node_schema import ProjectNodeSchemaV1

ProjectNodeData = Any


class NodeList(list):
    """Custom list that automatically sets parent reference when nodes are added."""

    def __init__(self, parent: "ProjectNode"):
        super().__init__()
        self._parent = parent

    def append(self, item: "ProjectNode") -> None:
        item._parent = self._parent
        super().append(item)

    def insert(self, index: SupportsIndex, item: "ProjectNode") -> None:
        item._parent = self._parent
        super().insert(index, item)

    def extend(self, items: Iterable["ProjectNode"]) -> None:
        for item in items:
            item._parent = self._parent
        super().extend(items)

    def __setitem__(self, key, item: "ProjectNode") -> None:  # type: ignore[override]
        if isinstance(item, ProjectNode):
            item._parent = self._parent
        super().__setitem__(key, item)


class ProjectNode(ProjectNodeSchemaV1):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)
    _parent: Self | None = PrivateAttr(default=None)

    @classmethod
    def model_validate(cls, *args, **kwargs) -> Self:
        node = super().model_validate(*args, **kwargs)
        cls._setup_parent_references(node)
        return node

    @classmethod
    def _setup_parent_references(cls, node: "ProjectNode") -> None:
        """Recursively setup parent references for all nested nodes."""
        nodes_data = node.nodes[:]
        node.nodes = NodeList(node)
        for child_node in nodes_data:
            node.nodes.append(child_node)
            cls._setup_parent_references(child_node)

    @field_validator("name", "type", mode="before")
    @classmethod
    def _strip_name_and_type(cls, v: str) -> str:
        return v.strip()

    @property
    def full_name(self) -> list[str]:
        """Get the full path name by traversing up through all parents."""
        path_parts = []
        current: ProjectNode | None = self

        while current is not None:
            path_parts.append(current.name)
            current = current._parent

        # Reverse to get root -> child order
        path_parts.reverse()
        return path_parts
