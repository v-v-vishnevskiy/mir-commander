from PySide6.QtCore import QSettings, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QMainWindow

from mir_commander.widgets import About


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle("Mir Commander")

        self.settings = QSettings("VishnevskiyGroup", "MirCommander")

        # Menu Bar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu(self.tr("File"))
        self.help_menu = self.menubar.addMenu(self.tr("Help"))
        self.setup_menubar()

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage(self.tr("Ready"))

        self._restore_settings()

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

    def _save_settings(self):
        self.settings.setValue("mainwindow/geometry", self.saveGeometry())

    def _restore_settings(self):
        # Window dimensions
        geometry = self.settings.value("mainwindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            geometry = self.screen().availableGeometry()
            self.setGeometry(
                geometry.width() * 0.25,
                geometry.height() * 0.25,
                geometry.width() * 0.5,
                geometry.height() * 0.5,
            )

    @Slot()
    def quit_app(self, *args, **kwargs):
        self._save_settings()
        QApplication.quit()

    def closeEvent(self, *args, **kwargs):
        self._save_settings()
