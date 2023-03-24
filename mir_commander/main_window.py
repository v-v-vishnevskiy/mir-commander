from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow

from mir_commander.widgets import About


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Mir Commander")

        # Menu Bar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu(self.tr("File"))
        self.help_menu = self.menubar.addMenu(self.tr("Help"))
        self.setup_menubar()

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage(self.tr("Ready"))

        # Window dimensions
        geometry = self.screen().availableGeometry()
        self.setGeometry(
            geometry.width() * 0.15,
            geometry.width() * 0.15,
            geometry.width() * 0.5,
            geometry.height() * 0.5,
        )

    def setup_menubar(self):
        self._setup_menubar_file()
        self._setup_menubar_help()

    def _setup_menubar_file(self):
        self.file_menu.addAction(self._quit_action())

    def _setup_menubar_help(self):
        self.help_menu.addAction(self._about_action())

    def _quit_action(self) -> QAction:
        action = QAction(self.tr("Quit"), self)
        action.setShortcut(QKeySequence.Quit)
        action.triggered.connect(self.quit_app)
        return action

    def _about_action(self) -> QAction:
        action = QAction(self.tr("About"), self)
        action.triggered.connect(About(self).show)
        return action

    @Slot()
    def quit_app(self, *args, **kwargs):
        QApplication.quit()
