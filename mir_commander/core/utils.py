import logging
from pathlib import Path

from .errors import LoadProjectError
from .parsers import load_file
from .project import Project

logger = logging.getLogger(__name__)


def load_project(path: Path) -> tuple[Project, list[str]]:
    """
    Returns (re)created project and a list of messages corresponding to the process of project loading.
    """

    path = path.resolve()

    # If this is a file, then it may be from some other program
    # and we can try to import its data and create a project on the fly.
    if path.is_file():
        logs: list[str] = []
        project = Project()
        project.data.items.append(load_file(path, logs))
        project.config.name = path.stem

        # for fitem in flagged_items:
        #     if fitem.get("view"):
        #         project.mark_item_to_view(fitem["itempar"])

        return project, logs
    else:
        msg = "Invalid path"
        logger.error(f"{msg}: {path}")
        raise LoadProjectError(msg, f"{msg}: {path}")
