"""
The FileManager has a high risk of getting an unpredictable error when working with third-party importers and exporters.
Be careful when developing this tool. Test it more thoroughly.
"""

import logging
from pathlib import Path

from mir_commander.plugin_system.file_exporter import ExportFileError, FileExporter
from mir_commander.plugin_system.file_importer import FileImporter, ImportFileError

from .errors import FileExporterNotFoundError, FileImporterNotFoundError
from .models import Item

logger = logging.getLogger("Core.FileManager")


class FileManager:
    def __init__(self):
        self._file_importers: list[FileImporter] = []
        self._file_exporters: list[FileExporter] = []

    def _get_importer_id(self, file_importer: FileImporter) -> str:
        return file_importer.__class__.__name__

    def _get_exporter_id(self, file_exporter: FileExporter) -> str:
        return file_exporter.__class__.__name__

    def _get_file_importers_by_extension(self, extension: str) -> list[FileImporter]:
        result = []
        for file_importer in self._file_importers:
            if extension in file_importer.get_extensions():
                result.append(file_importer)
        return result

    def _get_file_importer_by_id(self, importer_id: str) -> FileImporter:
        for file_importer in self._file_importers:
            if importer_id == self._get_importer_id(file_importer):
                return file_importer
        raise FileImporterNotFoundError()

    def _get_file_exporter_by_id(self, exporter_id: str) -> FileExporter:
        for file_exporter in self._file_exporters:
            if exporter_id == self._get_exporter_id(file_exporter):
                return file_exporter
        raise FileExporterNotFoundError()

    def register_file_importer(self, file_importer: FileImporter):
        # TODO: validate file_importer
        logger.debug("%s importer registered", file_importer.get_name())
        self._file_importers.append(file_importer)

    def register_file_exporter(self, file_exporter: FileExporter):
        # TODO: validate file_exporter
        logger.debug("%s exporter registered", file_exporter.get_name())
        self._file_exporters.append(file_exporter)

    def get_file_importers(self) -> list[tuple[str, FileImporter]]:
        return [(self._get_importer_id(item), item) for item in self._file_importers]

    def get_file_exporters(self) -> list[tuple[str, FileExporter]]:
        return [(self._get_exporter_id(item), item) for item in self._file_exporters]

    def import_file(self, path: Path, logs: list[str], importer_id: str = "") -> Item:
        if importer_id != "":
            return self._get_file_importer_by_id(importer_id).read(path, logs)

        file_extension = path.suffix.lstrip(".")
        file_importers = self._get_file_importers_by_extension(file_extension)

        if len(file_importers) == 0:
            raise FileImporterNotFoundError()

        for file_importer in file_importers:
            try:
                return file_importer.read(path, logs)
            except ImportFileError as e:
                logger.error("Can't import file with %s: %s", file_importer.__class__.__name__, e)
            except Exception as e:
                logger.error("%s(name=%s) error: %s", file_importer.__class__.__name__, file_importer.get_name(), e)
        raise ImportFileError()

    def export_item(self, item: Item, path: Path, nested: bool, exporter_id: str):
        exporter = self._get_file_exporter_by_id(exporter_id)
        try:
            exporter.write(item, path, nested)
        except Exception as e:
            logger.error("%s(name=%s) error: %s", exporter.__class__.__name__, exporter.get_name(), e)
            raise ExportFileError()
