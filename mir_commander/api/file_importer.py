from pathlib import Path
from typing import Callable

from pydantic import Field

from .plugin import Details, Plugin
from .project_node_schema import ProjectNodeSchema


class ImportFileError(Exception):
    pass


class InvalidFormatError(ImportFileError):
    pass


class FileImporterDetails(Details):
    extensions: list[str] = Field(default_factory=list, description="Extensions")
    read_function: Callable[[Path, list[str]], ProjectNodeSchema] = Field(description="Read function")


class FileImporterPlugin(Plugin):
    details: FileImporterDetails
