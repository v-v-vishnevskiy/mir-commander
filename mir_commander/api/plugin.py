from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Metadata(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Name of the plugin")
    version: tuple[int, int, int]
    description: str = Field(min_length=1, description="Description of the plugin")
    author: str = Field(min_length=1, description="Author of the plugin")
    contacts: str = Field(min_length=1, description="Email or URL of the plugin author")
    license: str = Field(min_length=1, description="License of the plugin")


class Dependency(BaseModel):
    name: str = Field(min_length=1, description="Name of the dependency")
    version: str = ""
    type: Literal["python_package"]


class Details(BaseModel):
    pass


class Plugin(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    id: str = Field(min_length=1, description="ID of the plugin")
    metadata: Metadata = Field(description="Metadata of the plugin")
    dependencies: list[Dependency] = Field(default_factory=list, description="Dependencies of the plugin")
    details: Details = Field(description="Details of the plugin")
