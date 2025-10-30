from typing import Any

from pydantic import ConfigDict, field_validator

from mir_commander.plugin_system.project_node_schema import ProjectNodeSchemaV1

ProjectNodeData = Any


class ProjectNode(ProjectNodeSchemaV1):
    model_config = ConfigDict(extra="forbid", strict=True, from_attributes=True)

    @field_validator("name", "type", mode="before")
    @classmethod
    def _strip_name_and_type(cls, v: str) -> str:
        return v.strip()
