import logging
from pathlib import Path

from mir_commander import errors
from mir_commander.parsers import load_file

from .base import Project
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
    else:
        msg = "Invalid path"
        logger.error(f"{msg}: {path}")
        raise errors.LoadProjectError(msg, f"{msg}: {path}")
