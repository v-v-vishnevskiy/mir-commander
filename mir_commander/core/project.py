import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from mir_commander.api.file_importer import ImportFileError
from mir_commander.api.project_node_schema import ProjectNodeSchemaV1

from .config import ProjectConfig
from .errors import LoadProjectError
from .file_manager import file_manager
from .project_node import ProjectNode
from .project_node_registry import project_node_registry

logger = logging.getLogger("Core.Project")


class Project:
    def __init__(self, path: Path, temporary: bool = False):
        self.path = path
        self._is_temporary = temporary
        self._nodes: list[ProjectNode] = []
        self.config = ProjectConfig.load(path / "config.yaml")

        self._load_project()

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
            node = ProjectNode.model_validate(raw_node)
            self._convert_raw_data(node)
            return node
        except ValidationError as e:
            raise ImportFileError(f"FileImporter returned invalid data: {e}")

    def _convert_raw_data(self, node: ProjectNode):
        if node.data is not None:
            model_class = project_node_registry.get(node.type).get_model_class()
            if model_class is not None:
                node.data = model_class.model_validate(node.data)
        for child_node in node.nodes:
            self._convert_raw_data(child_node)

    def import_files(self, files: list[Path], logs: list[str], parent: ProjectNode | None = None) -> list[ProjectNode]:
        nodes = []
        for file in files:
            try:
                nodes.append(self.import_file(file, logs, parent))
            except Exception as e:
                logger.error("Failed to import file %s: %s", file, e)
                logs.append(f"Failed to import file {file}: {e}")
        return nodes

    def import_file(self, path: Path, logs: list[str], parent: ProjectNodeSchemaV1 | None = None) -> ProjectNode:
        raw_node = file_manager.import_file(path, logs)
        project_node = self._convert_raw_node(raw_node)
        if parent is not None:
            parent.nodes.append(project_node)
        else:
            self._nodes.append(project_node)
        self.save()
        return project_node

    def export_file(self, node: ProjectNodeSchemaV1, exporter_name: str, path: Path, format_settings: dict[str, Any]):
        file_manager.export_file(node=node, exporter_name=exporter_name, path=path, format_settings=format_settings)

    def save(self):
        if not self.is_temporary:
            self.config.dump()
