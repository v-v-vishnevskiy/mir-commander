import logging

from mir_commander.core import project_nodes
from mir_commander.core.errors import ProjectNodeRegistrationError
from mir_commander.core.project_node_registry import project_node_registry

logger = logging.getLogger("Startup.ProjectNodes")


def startup():
    for item in project_nodes.__all__:
        project_node_data_class = project_nodes.__getattribute__(item)
        try:
            project_node_registry.register(project_node_data_class())
        except ProjectNodeRegistrationError as e:
            logger.error("Failed to register ProjectNode: %s", e)
