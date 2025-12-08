import argparse
import os
import platform
import sys
from pathlib import Path

from . import __version__
from .core import logging, plugins_loader
from .core.consts import DIR, FROZEN
from .ui.application import Application

PLATFORM = platform.system().lower()
logger = logging.getLogger("Main")


def _setup_working_directory():
    if FROZEN and PLATFORM == "darwin" and Path.cwd() == Path("/"):
        os.chdir(Path.home())


def _setup_cli_commands():
    if PLATFORM not in ("darwin", "linux") or FROZEN is False:
        return

    executable = Path(sys.executable)
    zshrc = Path.home() / ".zshrc"
    bashrc = Path.home() / ".bashrc"
    mircmd = DIR.MIRCMD_BIN / "mircmd"

    if not DIR.MIRCMD_BIN.exists():
        DIR.MIRCMD_BIN.mkdir(parents=True, exist_ok=True)

    for rc in (zshrc, bashrc):
        if rc.exists() and f'export PATH="{DIR.MIRCMD_BIN}:$PATH"' not in rc.read_text():
            with rc.open("a") as f:
                f.write(f'\nexport PATH="{DIR.MIRCMD_BIN}:$PATH" # Added by Mir Commander App\n')

    if PLATFORM == "darwin":
        if executable.is_relative_to("/Applications/Mir Commander.app") is False:
            return

    if not mircmd.exists():
        if PLATFORM == "darwin":
            os.symlink(executable, mircmd)
        elif PLATFORM == "linux":
            pass


def main():
    parser = argparse.ArgumentParser(prog="Mir Commander")
    parser.add_argument(
        "files", type=Path, default=[], nargs="*", help="Path to import files. Will be opened in a temporary project."
    )
    parser.add_argument("-p", "--project", type=Path, help="Path to project directory")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}", help="Show version and exit"
    )
    args = parser.parse_args()

    if not DIR.HOME_MIRCMD.exists():
        DIR.HOME_MIRCMD.mkdir(parents=True, exist_ok=True)

    if not DIR.MIRCMD_PLUGINS.exists():
        DIR.MIRCMD_PLUGINS.mkdir(parents=True, exist_ok=True)

    if not DIR.MIRCMD_LOGS.exists():
        DIR.MIRCMD_LOGS.mkdir(parents=True, exist_ok=True)

    logging.setup()

    logger.debug("Starting Mir Commander ...")

    _setup_cli_commands()
    _setup_working_directory()

    app = Application([])

    logger.debug("Loading built-in plugins ...")
    resources = plugins_loader.load_from_directory(DIR.INTERNAL_PLUGINS)
    app.register_plugin_resources(resources)

    logger.debug("Loading external plugins ...")
    resources = plugins_loader.load_from_directory(DIR.MIRCMD_PLUGINS, skip_authors=["builtin"])
    app.register_plugin_resources(resources)

    if args.files:
        sys.exit(app.open_temporary_project(args.files))
    elif args.project:
        sys.exit(app.open_project(args.project))
    else:
        sys.exit(app.open_empty_project())
