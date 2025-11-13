import argparse
import sys
from pathlib import Path

from .core import logging, plugins_loader
from .ui.application import Application
from .core.consts import DIR

logger = logging.getLogger("Main")


def run():
    if not DIR.HOME_CONFIG.exists():
        DIR.HOME_CONFIG.mkdir(parents=True, exist_ok=True)

    if not DIR.HOME_PLUGINS.exists():
        DIR.HOME_PLUGINS.mkdir(parents=True, exist_ok=True)

    logging.setup()

    logger.debug("Starting Mir Commander ...")

    app = Application([])

    logger.debug("Loading built-in plugins ...")
    plugins_loader.load_from_directory(DIR.INTERNAL_PLUGINS)

    logger.debug("Loading external plugins ...")
    plugins_loader.load_from_directory(DIR.HOME_PLUGINS, skip_authors=["builtin"])

    parser = argparse.ArgumentParser(prog="Mir Commander")
    parser.add_argument(
        "files", type=Path, default=[], nargs="*", help="Path to import files. Will be opened in a temporary project."
    )
    parser.add_argument("-p", "--project", type=Path, help="Path to project directory")
    args = parser.parse_args()

    if args.files:
        sys.exit(app.open_temporary_project(args.files))
    elif args.project:
        sys.exit(app.open_project(args.project))
    else:
        sys.exit(app.open_recent_projects_dialog())


if __name__ == "__main__":
    run()
