from pydantic import Field

from .plugin import Details, Plugin


class ProjectNodeDetails(Details):
    type: str = Field(min_length=1, max_length=255, description="Type identifier (e.g., 'atomic_coordinates')")
    icon_path: str = Field(min_length=1, description="Path to the icon file")


class ProjectNodePlugin(Plugin):
    details: ProjectNodeDetails
