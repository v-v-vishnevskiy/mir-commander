"""
The FileManager has a high risk of getting an unpredictable error when working with third-party importers and exporters.
Be careful when developing this tool. Test it more thoroughly.
"""

import logging
from pathlib import Path
from typing import Any

from mir_commander.plugin_system.file_importer import FileImporter, ImportFileError
from mir_commander.plugin_system.item_exporter import ExportItemError, ItemExporter

from .errors import FileImporterNotFoundError, ItemExporterNotFoundError
from .models import Item

logger = logging.getLogger("Core.FileManager")


class FileManager:
    def __init__(self):
        self._file_importers: list[FileImporter] = []
        self._item_exporters: list[ItemExporter] = []

    def _get_importer_id(self, file_importer: FileImporter) -> str:
        return file_importer.__class__.__name__

    def _get_exporter_id(self, file_exporter: ItemExporter) -> str:
        return file_exporter.__class__.__name__

    def _get_file_importers_by_extension(self, extension: str) -> list[FileImporter]:
        specific = []
        universal = []
        for file_importer in self._file_importers:
            if extension in file_importer.get_extensions():
                specific.append(file_importer)
            elif "*" in file_importer.get_extensions():
                universal.append(file_importer)
        return specific + universal

    def _get_file_importer_by_name(self, name: str) -> FileImporter:
        for file_importer in self._file_importers:
            if name == file_importer.get_name():
                return file_importer
        raise FileImporterNotFoundError()

    def _get_item_exporter_by_name(self, name: str) -> ItemExporter:
        for item_exporter in self._item_exporters:
            if name == item_exporter.get_name():
                return item_exporter
        raise ItemExporterNotFoundError()

    def register_file_importer(self, file_importer: FileImporter):
        # TODO: validate file_importer
        logger.debug("%s importer registered", file_importer.get_name())
        self._file_importers.append(file_importer)

    def register_item_exporter(self, item_exporter: ItemExporter):
        # TODO: validate file_exporter
        logger.debug("%s exporter registered", item_exporter.get_name())
        self._item_exporters.append(item_exporter)

    def get_file_importers(self) -> list[FileImporter]:
        return self._file_importers[:]

    def get_item_exporters(self) -> list[ItemExporter]:
        return self._item_exporters[:]

    def import_file(self, path: Path, logs: list[str], importer_name: str = "") -> Item:
        if importer_name != "":
            return self._get_file_importer_by_name(importer_name).read(path, logs)

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
                logger.error('%s(name="%s") error: %s', file_importer.__class__.__name__, file_importer.get_name(), e)
        raise ImportFileError()

    def export_item(self, item: Item, exporter_name: str, path: Path, format_settings: dict[str, Any]):
        exporter = self._get_item_exporter_by_name(exporter_name)
        try:
            exporter.write(item, path, format_settings)
        except ExportItemError as e:
            raise e
        except Exception as e:
            raise ExportItemError(f"Unexpected exporter error - {e}")
