from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field


class AutoOpenConfig(BaseModel):
    """Configuration for automatically opening a node in a program after import."""

    model_config = ConfigDict(extra="forbid", strict=True)

    program: str = Field(min_length=1, description="Name of the program to open the node with")
    params: dict[str, Any] = Field(default_factory=dict, description="Optional parameters to pass to the program")


class ProjectNodeSchemaV1(BaseModel):
    """
    Base model for project tree nodes.

    This is the public API for plugin developers.
    Use this model when creating file importers/exporters.

    Examples:
        # Open with default program
        node = ProjectNodeSchemaV1(
            name="Water Molecule",
            type="molecule",
            data={"atomic_num": [1, 8, 1], ...},
            auto_open=True,
        )

        # Open with specific program
        node = ProjectNodeSchemaV1(
            name="Water Molecule",
            type="molecule",
            auto_open=[AutoOpenConfig(program="molecular_visualizer")],
        )

        # Open in multiple programs
        node = ProjectNodeSchemaV1(
            name="Water Molecule",
            type="molecule",
            auto_open=[
                AutoOpenConfig(program="molecular_visualizer"),
                AutoOpenConfig(program="cartesian_editor", params={"mode": "edit"}),
            ],
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
    auto_open: bool | list[AutoOpenConfig] = Field(
        default=False,
        description=(
            "Whether to automatically open this node after import. "
            "Can be True for default program, or list of AutoOpenConfig to open in specific programs"
        ),
    )

    @property
    def full_name(self) -> list[str]:
        return []
