import sys

from mir_commander.application import Application
from mir_commander.main_window import MainWindow

if __name__ == "__main__":
    app = Application([])
    mainWindow = MainWindow(app)
    mainWindow.show()
    sys.exit(app.exec())
