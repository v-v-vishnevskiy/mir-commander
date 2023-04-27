import logging
import os

from cclib.io import ccread

from mir_commander import exceptions
from mir_commander.data_structures.molecule import Molecule as MolData
from mir_commander.projects.base import Project
from mir_commander.projects.molecule import Molecule as MolProject
from mir_commander.utils.config import Config
from mir_commander.utils.item import Item

logger = logging.getLogger(__name__)


def import_file(path: str) -> Project:
    # Use here cclib for parsing files
    data = ccread(path)
    if data is None:
        msg = "cclib cannot determine the format of file"
        logger.error(f"{msg}: {path}")
        raise exceptions.LoadProject(msg, f"{msg}: {path}")

    molproj = MolProject(path, Config(""))
    moldata = MolData(data.natom, data.atomnos)
    molitem = Item("Molecule", "", moldata)
    molproj.root_item.appendRow(molitem)

    # TODO: add atoms

    return molproj


def load_project(path: str, app_config_dir: str) -> Project:
    path = os.path.normpath(path)

    # If this is a file, then it may be from some other program
    # and we can try to import its data and create a project on the fly.
    if os.path.isfile(path):
        project = import_file(path)
        return project
    # If this is a directory, then we expect a Mir Commander project
    elif os.path.isdir(path):
        config_path = os.path.join(path, ".mircmd", "config.yaml")
        # If config file does not exist in .mircmd
        if not os.path.isfile(config_path):
            msg = "Config file does not exist"
            logger.error(f"{msg}: {config_path}")
            raise exceptions.LoadProject(msg, f"{msg}: {config_path}")
        # or if we are trying to open user config dir
        elif config_path == os.path.join(app_config_dir, "config"):
            msg = "Mir Commander user configuration directory cannot contain project file(s)"
            logger.error(msg)
            raise exceptions.LoadProject(msg)

        config = Config(config_path)
        project_type = config["type"]
        if project_type == "Molecule":
            return MolProject(path, config)
        else:
            msg = "Invalid project type"
            logger.error(f"{msg}: {project_type}")
            raise exceptions.LoadProject(msg, f"{msg}: {project_type}")
    else:
        msg = "Invalid path"
        logger.error(f"{msg}: {path}")
        raise exceptions.LoadProject(msg, f"{msg}: {path}")


__all__ = ["load_project"]
