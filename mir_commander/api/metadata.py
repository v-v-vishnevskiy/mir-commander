from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """
    Metadata for plugins.
    """

    name: str = Field(min_length=1, max_length=255, description="Name of the plugin")
    version: tuple[int, int, int]
    description: str = Field(min_length=1, description="Description of the plugin")
    author: str = Field(min_length=1, description="Author of the plugin")
    email: str = Field(min_length=1, description="Email of the plugin")
    url: str = ""
    license: str = Field(min_length=1, description="License of the plugin")
