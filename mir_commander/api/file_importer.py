from pathlib import Path
from typing import Callable

from pydantic import Field

from .plugin import Details, Plugin
from .project_node_schema import ProjectNodeSchemaV1


class ImportFileError(Exception):
    pass


class InvalidFormatError(ImportFileError):
    pass


class FileImporterDetails(Details):
    extensions: list[str] = Field(default_factory=list, description="Extensions")
    read_function: Callable[[Path, list[str]], ProjectNodeSchemaV1] = Field(description="Read function")


class FileImporterPlugin(Plugin):
    details: FileImporterDetails
