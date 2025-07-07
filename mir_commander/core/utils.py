from pathlib import Path

from .errors import LoadProjectError
from .project import Project


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
        project.import_file(path, logs)
        project.config.name = path.name

        return project, logs
    else:
        raise LoadProjectError(f"Invalid path: {path}")
