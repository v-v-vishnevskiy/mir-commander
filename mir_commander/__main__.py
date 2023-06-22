import argparse
import shutil
import sys

from mir_commander.consts import DIR
from mir_commander.ui.application import Application


def create_config_dir():
    if not DIR.CONFIG.exists():
        shutil.copytree(DIR.DEFAULT_CONFIGS, DIR.CONFIG)


if __name__ == "__main__":
    create_config_dir()

    parser = argparse.ArgumentParser(prog="Mir Commander")
    parser.add_argument("path", type=str, default="", nargs="?", help="Path to input file or project directory")
    args = parser.parse_args()

    app = Application([])
    app.fix_palette()
    sys.exit(app.run(args.path))
