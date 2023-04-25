import logging
import os

from PySide6.QtCore import QSettings

from mir_commander import exceptions
from mir_commander.projects.base import Project
from mir_commander.projects.molecule import Molecule

logger = logging.getLogger(__name__)


def load_project(path: str, app_config_dir: str) -> Project:
    path = os.path.normpath(path)

    if app_config_dir == os.path.join(path, ".mircmd"):
        msg = "Trying to open the application config file, not project"
        logger.error(msg)
        raise exceptions.LoadProject(msg)

    config_path = os.path.join(path, ".mircmd", "config")
    if not os.path.exists(config_path):
        msg = "Path to config file does not exist"
        logger.error(f"{msg}: {config_path}")
        raise exceptions.LoadProject(msg, f"{msg}: {config_path}")

    settings = QSettings(config_path, QSettings.Format.IniFormat)
    project_type = settings.value("type")
    if project_type == "Molecule":
        return Molecule(path)
    else:
        msg = "Undefined project type"
        logger.error(f"{msg}: {project_type}")
        raise exceptions.LoadProject(msg, f"{msg}: {project_type}")


__all__ = ["Molecule", "load_project"]
