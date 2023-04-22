import argparse
import sys

from mir_commander.application import Application

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Mir Commander")
    parser.add_argument("--project", default="", help="Path to project directory")
    args = parser.parse_args()

    app = Application([])
    sys.exit(app.run(args.project))
