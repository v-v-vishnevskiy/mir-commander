"""
The FileManager has a high risk of getting an unpredictable error when working with third-party importers and exporters.
Be careful when developing this tool. Test it more thoroughly.
"""

import logging
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from mir_commander.api.file_exporter import ExportFileError, FileExporterPlugin
from mir_commander.api.file_importer import FileImporterPlugin, ImportFileError, InvalidFormatError
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1

from .errors import FileExporterNotFoundError, FileExporterRegistrationError, FileImporterNotFoundError

logger = logging.getLogger("Core.FileManager")


class FormatSettingsDefaultProperty(BaseModel):
    type: Literal["property"]
    value: Literal["node.name", "node.full_name"]


class FormatSettingsDefaultLiteral(BaseModel):
    type: Literal["literal"]
    value: str | int | float | bool | list[str]


class BaseFormatSettings(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    default: Annotated[FormatSettingsDefaultProperty | FormatSettingsDefaultLiteral, Field(discriminator="type")]
    required: bool


class BoolTypeFormatSettings(BaseFormatSettings):
    type: Literal["bool"]


class TextTypeFormatSettings(BaseFormatSettings):
    type: Literal["text"]


class NumberTypeFormatSettings(BaseFormatSettings):
    type: Literal["number"]
    min: int
    max: int
    step: int


class ListTypeFormatSettings(BaseFormatSettings):
    type: Literal["list"]
    items: list[str] = Field(min_length=1)


FormatSettingsValidator = Annotated[
    BoolTypeFormatSettings | TextTypeFormatSettings | NumberTypeFormatSettings | ListTypeFormatSettings,
    Field(discriminator="type"),
]


format_settings_validator_adaptor = TypeAdapter[BaseFormatSettings](FormatSettingsValidator)


class FileManager:
    def __init__(self):
        self._importers: list[FileImporterPlugin] = []
        self._exporters: list[FileExporterPlugin] = []

    def _validate_exporter_settings_config(self, exporter: FileExporterPlugin):
        errors = []
        for i, config in enumerate(exporter.get_settings_config()):
            try:
                format_settings_validator_adaptor.validate_python(config)
            except ValidationError as e:
                errs = []
                for error in e.errors(include_url=False, include_context=False, include_input=False):
                    if loc := error.get("loc", tuple[str | int, ...]()):
                        field = f".{'.'.join(map(str, loc))}"
                    else:
                        field = ""
                    if error.get("type") == "model_type":
                        message = "Input should be a valid dictionary"
                    else:
                        message = error.get("msg", "Unknown error")
                    errs.append(f"`{i}{field}` -> {message}")
                errors.append("; ".join(errs))

        if len(errors) > 0:
            raise FileExporterRegistrationError(f"Invalid settings config: {'; '.join(errors)}")

        # TODO: validate other properties of exporter

    def _get_importers_by_extension(self, extension: str) -> list[FileImporterPlugin]:
        specific = []
        universal = []
        for importer in self._importers:
            if extension in importer.get_extensions():
                specific.append(importer)
            elif "*" in importer.get_extensions():
                universal.append(importer)
        return specific + universal

    def _get_importer_by_name(self, name: str) -> FileImporterPlugin:
        for importer in self._importers:
            if name == importer.get_name():
                return importer
        raise FileImporterNotFoundError()

    def _get_exporter_by_name(self, name: str) -> FileExporterPlugin:
        for exporter in self._exporters:
            if name == exporter.get_name():
                return exporter
        raise FileExporterNotFoundError()

    def register_importer(self, importer: FileImporterPlugin):
        # TODO: validate importer
        logger.debug("`%s` importer registered", importer.get_name())
        self._importers.append(importer)

    def register_exporter(self, exporter: FileExporterPlugin):
        self._validate_exporter_settings_config(exporter)
        logger.debug("`%s` exporter registered", exporter.get_name())
        self._exporters.append(exporter)

    def get_importers(self) -> list[FileImporterPlugin]:
        return self._importers[:]

    def get_exporters(self, type_name: str = "") -> list[FileExporterPlugin]:
        if type_name == "":
            return self._exporters[:]
        else:
            return [exporter for exporter in self._exporters if type_name in exporter.get_supported_node_types()]

    def import_file(self, path: Path, logs: list[str], importer_name: str = "") -> ProjectNodeSchemaV1:
        if importer_name != "":
            return self._get_importer_by_name(importer_name).read(path, logs)

        file_extension = path.suffix.lstrip(".")
        importers = self._get_importers_by_extension(file_extension)

        if len(importers) == 0:
            raise FileImporterNotFoundError()

        for importer in importers:
            try:
                return importer.read(path, logs)
            except InvalidFormatError:
                continue
            except ImportFileError as e:
                logger.error("Can't import file with %s: %s", importer.__class__.__name__, e)
            except Exception as e:
                logger.error("%s error: %s - %s", importer.__class__.__name__, e.__class__.__name__, e)
        raise ImportFileError()

    def export_file(self, node: ProjectNodeSchemaV1, exporter_name: str, path: Path, format_settings: dict[str, Any]):
        exporter = self._get_exporter_by_name(exporter_name)
        try:
            exporter.write(node, path, format_settings)
        except ExportFileError as e:
            raise e
        except Exception as e:
            raise ExportFileError(f"Unexpected exporter error - {e}")


file_manager = FileManager()
