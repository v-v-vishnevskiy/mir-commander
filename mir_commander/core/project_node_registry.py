import logging

from mir_commander.api.project_node import ProjectNodePlugin

from .errors import ProjectNodeNotFoundError, ProjectNodeRegistrationError

logger = logging.getLogger("Core.ProjectNodeRegistry")


class ProjectNodeRegistry:
    def __init__(self):
        self._registry: dict[str, ProjectNodePlugin] = {}

    def _validate_model(self, project_node: ProjectNodePlugin):
        if issubclass(project_node.__class__, ProjectNodePlugin) is False:
            raise ProjectNodeRegistrationError(
                f"{project_node.__class__.__name__} should be a subclass of ProjectNodePlugin"
            )

    def get_project_nodes(self) -> dict[str, ProjectNodePlugin]:
        return self._registry

    def register(self, project_node: ProjectNodePlugin):
        self._validate_model(project_node)

        self._registry[project_node.get_type()] = project_node
        logger.debug("`%s` registered", project_node.get_name())

    def get(self, node_type: str) -> ProjectNodePlugin:
        if node_type not in self._registry:
            raise ProjectNodeNotFoundError()
        return self._registry[node_type]


project_node_registry = ProjectNodeRegistry()
