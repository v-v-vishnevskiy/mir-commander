from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """
    Metadata for plugins.
    """

    name: str = Field(min_length=1, max_length=255, description="Name of the plugin")
    version: tuple[int, int, int]
    description: str = Field(min_length=1, description="Description of the plugin")
    author: str = Field(min_length=1, description="Author of the plugin")
    contacts: str = Field(min_length=1, description="Email or URL of the plugin author")
    license: str = Field(min_length=1, description="License of the plugin")
