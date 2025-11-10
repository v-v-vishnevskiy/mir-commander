from mir_commander.api.plugin_registry import PluginRegistry

from .cclib_importer import CCLibImporter
from .cfour_importer import CFourImporter
from .gaussian_cube_importer import GaussianCubeImporter
from .mdlmol2000_importer import MDLMolV2000Importer
from .unex_importer import UnexImporter
from .xyz_importer import XYZImporter


def register_plugins(registry: PluginRegistry):
    registry.register_file_importer(CCLibImporter())
    registry.register_file_importer(CFourImporter())
    registry.register_file_importer(GaussianCubeImporter())
    registry.register_file_importer(MDLMolV2000Importer())
    registry.register_file_importer(UnexImporter())
    registry.register_file_importer(XYZImporter())
