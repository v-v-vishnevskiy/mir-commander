import argparse
import os
import platform
import sys
from pathlib import Path

from .core import logging, plugins_loader
from .core.consts import DIR
from .ui.application import Application

logger = logging.getLogger("Main")


def _setup_working_directory():
    if getattr(sys, "frozen", False) and Path.cwd() == Path("/"):
        if platform.system().lower() == "darwin":
            os.chdir(Path.home())


def main():
    if not DIR.HOME_CONFIG.exists():
        DIR.HOME_CONFIG.mkdir(parents=True, exist_ok=True)

    if not DIR.HOME_PLUGINS.exists():
        DIR.HOME_PLUGINS.mkdir(parents=True, exist_ok=True)

    logging.setup()

    _setup_working_directory()

    logger.debug("Starting Mir Commander ...")

    app = Application([])

    logger.debug("Loading built-in plugins ...")
    resources = plugins_loader.load_from_directory(DIR.INTERNAL_PLUGINS)
    app.register_plugin_resources(resources)

    logger.debug("Loading external plugins ...")
    resources = plugins_loader.load_from_directory(DIR.HOME_PLUGINS, skip_authors=["builtin"])
    app.register_plugin_resources(resources)

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
        sys.exit(app.open_empty_project())
