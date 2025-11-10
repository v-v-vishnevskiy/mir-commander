from enum import Enum
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field


class ActionType(Enum):
    OPEN = "open"


class ProjectNodeSchemaV1(BaseModel):
    """
    Base model for project tree nodes.

    This is the public API for plugin developers.
    Use this model when creating file importers/exporters.

    Examples:
        node = ProjectNodeSchemaV1(
            name="Water Molecule",
            type="atomic_coordinates",
            AtomicCoordinates(atomic_num=[1, 8, 1], ...),
            actions=[ActionType.AUTO_OPEN],
        )
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=255, description="Display name of the node")
    type: str = Field(
        min_length=1, max_length=255, description="Type identifier (e.g., 'molecule', 'atomic_coordinates')"
    )
    data: Any = Field(default=None, description="Node-specific data")
    nodes: list[Self] = Field(default_factory=list, description="Nested nodes of the node")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    actions: list[ActionType] = Field(default_factory=list, description="Actions to perform on the node")

    @property
    def full_name(self) -> list[str]:
        return []
