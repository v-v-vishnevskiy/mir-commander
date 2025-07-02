import argparse
import logging
import sys
from pathlib import Path

from .ui.application import Application
from .utils.logging import init_logging

logger = logging.getLogger("main")


def run():
    parser = argparse.ArgumentParser(prog="Mir Commander")
    parser.add_argument("path", type=str, default="", nargs="?", help="Path to input file or project directory")
    args = parser.parse_args()

    init_logging()
    logger.debug("Starting Mir Commander ...")

    app = Application([])
    app.fix_palette()
    sys.exit(app.run(Path(args.path)))


if __name__ == "__main__":
    run()
