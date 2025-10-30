from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProjectNodeData = Any


class ProjectNode(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    name: str = Field(min_length=1, max_length=255)
    type: str = Field(min_length=1, max_length=255)
    data: ProjectNodeData = None
    nodes: list[Self] = []
    metadata: dict[str, Any] = {}

    @field_validator("name")
    @classmethod
    def _strip_name(cls, v: str) -> str:
        return v.strip()
