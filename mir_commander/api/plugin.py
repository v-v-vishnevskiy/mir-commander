from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class Metadata(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="Name of the plugin")
    version: tuple[int, int, int]
    description: str = Field(min_length=1, description="Description of the plugin")
    author: str = Field(min_length=1, description="Author of the plugin")
    contacts: str = Field(min_length=1, description="Email or URL of the plugin author")
    license: str = Field(min_length=1, description="License of the plugin")


class Details(BaseModel):
    pass


class Translation(BaseModel):
    filename: str
    prefix: str
    path: str


class Resource(BaseModel):
    path: Path = Field(description="Relative path to the resource file")
    translations: list[Translation] = Field(default_factory=list, description="Translations of the resource")


class Plugin(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    id: str = Field(min_length=1, description="ID of the plugin")
    metadata: Metadata = Field(description="Metadata of the plugin")
    details: Details = Field(description="Details of the plugin")
    resources: list[Resource] = Field(default_factory=list, description="Resources of the plugin")
