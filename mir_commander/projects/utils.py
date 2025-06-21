import logging
from pathlib import Path

from mir_commander import consts, errors
from mir_commander.parsers import load_file
from mir_commander.utils.config import Config

from .base import Project
from .molecule import Molecule
from .temporary import Temporary

logger = logging.getLogger(__name__)


def load_project(path: Path) -> tuple[Project, list[str]]:
    """
    Returns (re)created project and a list of messages corresponding to the process of project loading.
    """

    path = path.resolve()

    # If this is a file, then it may be from some other program
    # and we can try to import its data and create a project on the fly.
    if path.is_file():
        project = Temporary(path)
        project_root_item, flagged_items, messages = load_file(path)
        project.root_item.appendRow(project_root_item)

        for fitem in flagged_items:
            if fitem.get("view"):
                project.mark_item_to_view(fitem["itempar"])
            if fitem.get("expand"):
                project.mark_item_to_expand(fitem["itempar"])

        return project, messages
    # If this is a directory, then we expect a Mir Commander project
    elif path.is_dir():
        config_path = path / ".mircmd" / "config.yaml"
        # If config file does not exist in .mircmd
        if not config_path.is_file():
            msg = "Config file does not exist"
            logger.error(f"{msg}: {config_path}")
            raise errors.LoadProjectError(msg, f"{msg}: {config_path}")
        # or if we are trying to open user config dir
        elif config_path == consts.DIR.HOME_CONFIG / "config.yaml":
            msg = "Mir Commander user configuration directory cannot contain project file(s)"
            logger.error(msg)
            raise errors.LoadProjectError(msg)

        config = Config(config_path)
        project_type = config["type"]
        if project_type == "Molecule":
            return Molecule(path, config), []
        else:
            msg = "Invalid project type"
            logger.error(f"{msg}: {project_type}")
            raise errors.LoadProjectError(msg, f"{msg}: {project_type}")
    else:
        msg = "Invalid path"
        logger.error(f"{msg}: {path}")
        raise errors.LoadProjectError(msg, f"{msg}: {path}")
