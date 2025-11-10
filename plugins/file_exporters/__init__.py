from mir_commander.api.plugin_registry import PluginRegistry

from .xyz_exporter import XYZExporter


def register_plugins(registry: PluginRegistry):
    registry.register_file_exporter(XYZExporter())
