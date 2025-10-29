import logging

from mir_commander.core import FileManager, file_importers, item_exporters
from mir_commander.core.errors import FileImporterRegistrationError, ItemExporterRegistrationError

logger = logging.getLogger("Startup.FileManager")


def startup():
    file_manager = FileManager()

    for item_exporter in item_exporters.__all__:
        item_exporter_class = item_exporters.__getattribute__(item_exporter)
        try:
            file_manager.register_item_exporter(item_exporter_class())
        except ItemExporterRegistrationError as e:
            logger.error(f"Failed to register {item_exporter_class.__name__}: {e}")

    for file_importer in file_importers.__all__:
        file_importer_class = file_importers.__getattribute__(file_importer)
        try:
            file_manager.register_file_importer(file_importer_class())
        except FileImporterRegistrationError as e:
            logger.error(f"Failed to register {file_importer_class.__name__}: {e}")

    return file_manager
