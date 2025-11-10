from abc import abstractmethod
from pathlib import Path
from typing import Any

from .plugin import Plugin
from .project_node_schema import ProjectNodeSchemaV1


class ExportFileError(Exception):
    pass


class FileExporterPlugin(Plugin):
    """
    Base class for file exporter plugins.

    Example:
        class MyExporter(FileExporterPlugin):
            def get_name(self) -> str:
                return "My Format"

            def get_supported_node_types(self) -> list[str]:
                return ["molecule", "atomic_coordinates"]

            def get_extensions(self) -> list[str]:
                return ["my_format"]

            def get_settings_config(self) -> list[dict[str, Any]]:
                return [
                    {
                        "id": "title",
                        "label": "Title",
                        "type": "text",
                        "default": {"type": "property", "value": "node.name"},
                    }
                ]

            def write(self, node: ProjectNodeSchema, path: Path, format_settings: dict[str, Any]):
                with open(path, 'w') as f:
                    f.write(f"{format_settings.get('title', node.name)}\n")

            def get_metadata(self) -> Metadata:
                return Metadata(
                    name="My Format",
                    version=(1, 0, 0),
                    description="My Format",
                    author="My Name",
                    email="my@email.com",
                    url="https://my.url.com",
                    license="MIT",
                )
    """

    @abstractmethod
    def get_supported_node_types(self) -> list[str]: ...

    @abstractmethod
    def get_extensions(self) -> list[str]: ...

    @abstractmethod
    def get_settings_config(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def write(self, node: ProjectNodeSchemaV1, path: Path, format_settings: dict[str, Any]): ...
