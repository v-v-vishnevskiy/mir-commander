import logging
from pathlib import Path

from pydantic import ValidationError

from mir_commander.api.file_importer import ImportFileError
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1

from .config import BaseConfig
from .errors import LoadProjectError
from .file_manager import FileManager
from .plugins_registry import plugins_registry
from .project_node import ProjectNode

logger = logging.getLogger("Core.Project")


class ProjectConfig(BaseConfig):
    name: str = "Untitled"


class Project:
    def __init__(self, path: Path, temporary: bool = False):
        self.path = path
        self._is_temporary = temporary
        self._nodes: list[ProjectNode] = []
        self.config = ProjectConfig.load(path / "config.yaml")

        self._load_project()
        self._file_manager = FileManager(plugins_registry)

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_temporary(self) -> bool:
        return self._is_temporary

    @property
    def nodes(self) -> list[ProjectNode]:
        return self._nodes

    def _load_project(self):
        if self.is_temporary:
            return

        logger.info("Loading project: %s", self.path)

        self.path = self.path.resolve()
        if self.path.is_file():
            raise LoadProjectError(f"Invalid path: {self.path}")
        logger.info("Loading project completed")

    def _convert_raw_node(self, raw_node: ProjectNodeSchemaV1) -> ProjectNode:
        try:
            return ProjectNode.model_validate(raw_node)
        except ValidationError as e:
            raise ImportFileError(f"FileImporter returned invalid data: {e}")

    def import_files(self, files: list[Path], logs: list[str], parent: ProjectNode | None = None) -> list[ProjectNode]:
        nodes = []
        for file in files:
            try:
                nodes.append(self.import_file(file, logs, parent))
            except ImportFileError as e:
                msg = f"Failed to import file {file}: {e}"
                logs.append(msg)
                logger.error(msg)
        return nodes

    def import_file(self, path: Path, logs: list[str], parent: ProjectNodeSchemaV1 | None = None) -> ProjectNode:
        raw_node = self._file_manager.import_file(path, logs)
        project_node = self._convert_raw_node(raw_node)
        if parent is not None:
            parent.nodes.append(project_node)
        else:
            self._nodes.append(project_node)
        self.save()
        return project_node

    def save(self):
        if not self.is_temporary:
            self.config.dump()
