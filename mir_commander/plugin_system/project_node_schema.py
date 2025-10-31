from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field


class ProjectNodeSchemaV1(BaseModel):
    """
    Base model for project tree nodes.

    This is the public API for plugin developers.
    Use this model when creating file importers/exporters.

    Example:
        node = ProjectNodeSchemaV1(
            name="Water Molecule",
            type="molecule",
            data={"atomic_num": [1, 8, 1], ...},
        )
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=255, description="Display name of the node")
    type: str = Field(
        min_length=1, max_length=255, description="Type identifier (e.g., 'molecule', 'atomic_coordinates')"
    )
    data: Any = Field(default=None, description="Node-specific data, validated by ProjectNodeDataPlugin")
    nodes: list[Self] = Field(default_factory=list, description="Nested nodes of the node")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @property
    def full_name(self) -> list[str]:
        return []
