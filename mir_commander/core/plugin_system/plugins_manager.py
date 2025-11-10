from .file_registry import FileRegistry
from .program_registry import ProgramRegistry
from .project_node_registry import ProjectNodeRegistry


class PluginsManager:
    def __init__(self):
        self.file = FileRegistry()
        self.program = ProgramRegistry()
        self.project_node = ProjectNodeRegistry()


plugins_manager = PluginsManager()
