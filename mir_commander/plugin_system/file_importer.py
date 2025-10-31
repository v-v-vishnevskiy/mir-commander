from abc import ABC, abstractmethod
from pathlib import Path

from .metadata import Metadata
from .project_node_schema import ProjectNodeSchemaV1


class ImportFileError(Exception):
    pass


class InvalidFormatError(ImportFileError):
    pass


class FileImporterPlugin(ABC):
    """
    Base class for file importer plugins.

    Example:
        class MyImporter(FileImporterPlugin):
            def get_name(self) -> str:
                return "My Format"

            def get_extensions(self) -> list[str]:
                return ["my_format"]

            def read(self, path: Path, logs: list[str]) -> ProjectNodeSchema:
                return ProjectNodeSchema(name="My Format", type="my_format")

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
    def get_name(self) -> str: ...

    @abstractmethod
    def get_extensions(self) -> list[str]: ...

    @abstractmethod
    def read(self, path: Path, logs: list[str]) -> ProjectNodeSchemaV1: ...

    @abstractmethod
    def get_metadata(self) -> Metadata: ...
