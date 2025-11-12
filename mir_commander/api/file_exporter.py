from pathlib import Path
from typing import Annotated, Any, Callable, Literal

from pydantic import BaseModel, ConfigDict, Field

from .plugin import Details, Plugin
from .project_node_schema import ProjectNodeSchema


class ExportFileError(Exception):
    pass


class DefaultProperty(BaseModel):
    type: Literal["property"] = "property"
    value: Literal["node.name", "node.full_name"]


class DefaultLiteral(BaseModel):
    type: Literal["literal"] = "literal"
    value: str | int | float | bool | list[str]


class FormatParamsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    type: Literal["bool", "text", "number", "list"]

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    default: Annotated[DefaultProperty | DefaultLiteral, Field(discriminator="type")]
    required: bool


class BoolParam(FormatParamsConfig):
    type: Literal["bool"] = "bool"


class TextParam(FormatParamsConfig):
    type: Literal["text"] = "text"


class NumberParam(FormatParamsConfig):
    type: Literal["number"] = "number"
    min: int = Field(default=-2147483648)
    max: int = Field(default=2147483647)
    step: int = Field(default=1)


class ListParam(FormatParamsConfig):
    type: Literal["list"] = "list"
    items: list[str] = Field(min_length=1)


class FileExporterDetails(Details):
    supported_node_types: list[str] = Field(default_factory=list, description="Supported node types")
    extensions: list[str] = Field(default_factory=list, description="Extensions")
    format_params_config: list[
        Annotated[BoolParam | TextParam | NumberParam | ListParam, Field(discriminator="type")]
    ] = Field(default_factory=list, description="Format params config")
    write_function: Callable[[ProjectNodeSchema, Path, dict[str, Any]], None] = Field(description="Write function")


class FileExporterPlugin(Plugin):
    details: FileExporterDetails
