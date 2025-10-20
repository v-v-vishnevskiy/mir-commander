import argparse
import logging
import sys
from pathlib import Path

from mir_commander.ui.application import Application
from mir_commander.utils.consts import DIR
from mir_commander.utils.logging import init_logging

logger = logging.getLogger("Main")


def run():
    parser = argparse.ArgumentParser(prog="Mir Commander")
    parser.add_argument(
        "files", type=Path, default=[], nargs="*", help="Path to import files. Will be opened in a temporary project."
    )
    parser.add_argument("-p", "--project", type=Path, help="Path to project directory")
    args = parser.parse_args()

    if not DIR.HOME_CONFIG.exists():
        DIR.HOME_CONFIG.mkdir(parents=True, exist_ok=True)

    init_logging()
    logger.debug("Starting Mir Commander ...")

    app = Application([])
    app.fix_palette()

    if args.files:
        sys.exit(app.open_temporary_project(args.files))
    elif args.project:
        sys.exit(app.open_project(args.project))
    else:
        sys.exit(app.open_recent_projects_dialog())


if __name__ == "__main__":
    run()
