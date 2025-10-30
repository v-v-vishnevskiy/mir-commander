import logging

from mir_commander.core import file_exporters, file_importers
from mir_commander.core.errors import FileExporterRegistrationError, FileImporterRegistrationError
from mir_commander.core.file_manager import file_manager

logger = logging.getLogger("Startup.FileManager")


def startup():
    for item in file_exporters.__all__:
        file_exporter_class = file_exporters.__getattribute__(item)
        try:
            file_manager.register_exporter(file_exporter_class())
        except FileExporterRegistrationError as e:
            logger.error(f"Failed to register {file_exporter_class.__name__}: {e}")

    for item in file_importers.__all__:
        file_importer_class = file_importers.__getattribute__(item)
        try:
            file_manager.register_importer(file_importer_class())
        except FileImporterRegistrationError as e:
            logger.error(f"Failed to register {file_importer_class.__name__}: {e}")
