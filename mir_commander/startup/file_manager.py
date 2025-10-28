import logging

from mir_commander.core import FileManager, file_importers, item_exporters

logger = logging.getLogger("Startup.FileManager")


def startup():
    file_manager = FileManager()

    file_manager.register_item_exporter(item_exporters.XYZExporter())

    file_manager.register_file_importer(file_importers.UnexImporter())
    file_manager.register_file_importer(file_importers.CFourImporter())
    file_manager.register_file_importer(file_importers.MDLMolV2000Importer())
    file_manager.register_file_importer(file_importers.XYZImporter())
    file_manager.register_file_importer(file_importers.GaussianCubeImporter())
    file_manager.register_file_importer(file_importers.CCLibImporter())

    return file_manager
