from pathlib import Path

from .errors import LoadFileError, LoadProjectError
from .project import Project


def load_project(path: Path) -> Project:
    """
    Load project from a path.
    """

    path = path.resolve()

    # If this is a file, then it may be from some other program
    # and we can try to import its data and create a project on the fly.
    if path.is_file():
        raise LoadProjectError(f"Invalid path: {path}")
    else:
        return Project(path=path, temporary=False)


def create_temporary_project(files: list[Path]) -> tuple[Project, list[str]]:
    """
    Create a temporary project from a list of files.
    """

    logs: list[str] = []
    project = Project(path=Path(), temporary=True)
    for file in files:
        try:
            project.import_file(file, logs)
        except (FileNotFoundError, LoadFileError) as e:
            logs.append(f"Failed to import file {file}: {e}")

    if project.data.items:
        project.config.name = project.data.items[0].name

    return project, logs
