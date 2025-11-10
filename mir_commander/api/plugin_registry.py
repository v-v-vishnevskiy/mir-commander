from abc import ABC, abstractmethod

from .file_exporter import FileExporterPlugin
from .file_importer import FileImporterPlugin
from .program import ProgramPlugin
from .project_node import ProjectNodePlugin


class PluginRegistry(ABC):
    """
    Public interface for plugin registration.

    Plugin developers use this interface to register their plugins
    with the application.

    Example:
        def register_plugins(registry: PluginRegistry):
            registry.register_file_importer(MyImporter())
            registry.register_file_exporter(MyExporter())
            registry.register_program(MyProgram())
            registry.register_project_node(MyProjectNode())
    """

    @abstractmethod
    def register_file_importer(self, plugin: FileImporterPlugin) -> None:
        """
        Register a file importer plugin.

        Args:
            plugin: FileImporterPlugin instance to register
        """
        ...

    @abstractmethod
    def register_file_exporter(self, plugin: FileExporterPlugin) -> None:
        """
        Register a file exporter plugin.

        Args:
            plugin: FileExporterPlugin instance to register
        """
        ...

    @abstractmethod
    def register_program(self, plugin: ProgramPlugin) -> None:
        """
        Register a program plugin.

        Args:
            plugin: ProgramPlugin instance to register
        """
        ...

    @abstractmethod
    def register_project_node(self, plugin: ProjectNodePlugin) -> None:
        """
        Register a project node type plugin.

        Args:
            plugin: ProjectNodePlugin instance to register
        """
        ...
