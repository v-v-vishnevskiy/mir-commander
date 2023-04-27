import logging
import os

from mir_commander import exceptions
from mir_commander.projects.base import Project
from mir_commander.projects.molecule import Molecule
from mir_commander.utils.config import Config

logger = logging.getLogger(__name__)


def load_project(path: str, app_config_dir: str) -> Project:
    path = os.path.normpath(path)

    if app_config_dir == os.path.join(path, ".mircmd"):
        msg = "Trying to open the application config file, not project"
        logger.error(msg)
        raise exceptions.LoadProject(msg)

    config_path = os.path.join(path, ".mircmd", "config.yaml")
    if not os.path.exists(config_path):
        msg = "Path to config file does not exist"
        logger.error(f"{msg}: {config_path}")
        raise exceptions.LoadProject(msg, f"{msg}: {config_path}")

    config = Config(config_path)
    project_type = config["type"]
    if project_type == "Molecule":
        return Molecule(path, config)
    else:
        msg = "Undefined project type"
        logger.error(f"{msg}: {project_type}")
        raise exceptions.LoadProject(msg, f"{msg}: {project_type}")


__all__ = ["Molecule", "load_project"]
