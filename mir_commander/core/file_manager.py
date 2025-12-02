import logging
from pathlib import Path
from typing import Any

from mir_commander.api.file_exporter import ExportFileError, FileExporterPlugin
from mir_commander.api.file_importer import FileImporterPlugin, ImportFileError, InvalidFormatError
from mir_commander.api.project_node_schema import ProjectNodeSchema
from mir_commander.core.errors import PluginDisabledError, PluginNotFoundError

from .plugins_registry import PluginItem, PluginsRegistry

logger = logging.getLogger("Core.FileManager")


class FileManager:
    def __init__(self, plugins_registry: PluginsRegistry):
        self._plugins_registry = plugins_registry

    def _get_importers_by_extension(self, extension: str) -> list[FileImporterPlugin]:
        specific = []
        universal = []
        for item in self._plugins_registry.file_importer.get_all():
            if item.enabled is False:
                continue
            plugin = item.plugin
            if extension in plugin.details.extensions:
                specific.append(plugin)
            elif "*" in plugin.details.extensions:
                universal.append(plugin)
        return specific + universal

    def get_exporters(self, node_type: str = "") -> list[PluginItem[FileExporterPlugin]]:
        if node_type == "":
            result = []
            for item in self._plugins_registry.file_exporter.get_all():
                if item.enabled:
                    result.append(item)
            return result
        else:
            result = []
            for item in self._plugins_registry.file_exporter.get_all():
                if item.enabled and node_type in item.plugin.details.supported_node_types:
                    result.append(item)
            return result

    def import_file(self, path: Path, logs: list[str], importer_name: str = "") -> ProjectNodeSchema:
        if importer_name != "":
            try:
                return self._plugins_registry.file_importer.get(importer_name).details.read_function(path, logs)
            except (PluginNotFoundError, PluginDisabledError):
                raise ImportFileError("Importer not found")

        file_extension = path.suffix.lstrip(".")
        importers = self._get_importers_by_extension(file_extension)

        if len(importers) == 0:
            raise ImportFileError("No importers found for this file")

        for importer in importers:
            try:
                return importer.details.read_function(path, logs)
            except InvalidFormatError:
                continue
            except ImportFileError as e:
                logger.error("`%s` file importer error: %s", importer.metadata.name, e)
            except Exception as e:
                logger.error("%s: %s", importer.__class__.__name__, e)
        raise ImportFileError("No importers can handle this file")

    def export_file(self, node: ProjectNodeSchema, exporter_id: str, path: Path, format_params: dict[str, Any]):
        try:
            exporter = self._plugins_registry.file_exporter.get(exporter_id)
        except (PluginNotFoundError, PluginDisabledError):
            raise ExportFileError("Exporter not found")

        try:
            exporter.details.write_function(node, path, format_params)
        except Exception as e:
            raise ExportFileError(str(e))
