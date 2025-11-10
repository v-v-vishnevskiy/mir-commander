from mir_commander.api.file_exporter import FileExporterPlugin
from mir_commander.api.file_importer import FileImporterPlugin
from mir_commander.api.plugin_registry import PluginRegistry
from mir_commander.api.program import ProgramPlugin
from mir_commander.api.project_node import ProjectNodePlugin
from mir_commander.ui.program_manager import program_manager

from .file_manager import file_manager
from .project_node_registry import project_node_registry


class PluginRegistryAdapter(PluginRegistry):
    """
    Adapter that implements PluginRegistry protocol.

    This adapter bridges the public API (mir_commander.api) with the internal
    implementation (core and ui modules). It delegates plugin registration to
    the appropriate internal managers.
    """

    def register_file_importer(self, plugin: FileImporterPlugin) -> None:
        """Register a file importer plugin."""
        file_manager.register_importer(plugin)

    def register_file_exporter(self, plugin: FileExporterPlugin) -> None:
        """Register a file exporter plugin."""
        file_manager.register_exporter(plugin)

    def register_program(self, plugin: ProgramPlugin) -> None:
        """Register a program plugin."""
        program_manager.register(plugin)

    def register_project_node(self, plugin: ProjectNodePlugin) -> None:
        """Register a project node type plugin."""
        project_node_registry.register(plugin)


plugin_registry = PluginRegistryAdapter()
