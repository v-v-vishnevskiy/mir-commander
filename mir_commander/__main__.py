import argparse
import sys

from mir_commander.ui.application import Application

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Mir Commander")
    parser.add_argument("path", type=str, default="", nargs="?", help="Path to input file or project directory")
    args = parser.parse_args()

    app = Application([])
    sys.exit(app.run(args.path))
