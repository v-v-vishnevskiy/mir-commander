import logging
import os

from PySide6.QtCore import QSettings

from mir_commander import exceptions
from mir_commander.projects.base import Project
from mir_commander.projects.molecule import Molecule

logger = logging.getLogger(__name__)


def load_project(path: str) -> Project:
    path = os.path.normpath(path)
    config_path = os.path.join(path, ".mircmd", "config")

    if not os.path.exists(config_path):
        msg = "Project config file is not exist"
        logger.error(f"{msg} for {path}")
        raise exceptions.LoadProject(msg)

    settings = QSettings(config_path, QSettings.Format.IniFormat)
    project_type = settings.value("type")
    if project_type == "Molecule":
        return Molecule(path)
    else:
        logger.error(f"Undefined project type: {project_type}")
        raise exceptions.LoadProject("Undefined project type")


__all__ = ["Molecule", "load_project"]
