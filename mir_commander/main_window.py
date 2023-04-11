import os

from PySide6.QtCore import QResource, Qt, Slot
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMdiArea

from mir_commander.application import Application
from mir_commander.utils.widget import Translator
from mir_commander.widgets import About, Settings, dock_widget


class MainWindow(Translator, QMainWindow):
    """The class of the main window.

    It must inherit Translator since in the main window we have
    UI elements, which may transtaled on the fly.
    For this, a retranslate_ui method must be implemented!
    """

    def __init__(self, app: Application):
        QMainWindow.__init__(self, None)
        self.app = app
        self.settings = app.settings

        QResource.registerResource(os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "general.rcc"))

        self.setWindowTitle("Mir Commander")
        self.setWindowIcon(QIcon(":/icons/general/app.svg"))

        # Mdi area as a central widget
        self.mdi_area = QMdiArea()
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdi_area)

        # Settings
        self._restore_settings()

        # Menu Bar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu(self.tr("File"))
        self.view_menu = self.menubar.addMenu(self.tr("View"))
        self.help_menu = self.menubar.addMenu(self.tr("Help"))
        self.setup_menubar()

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage(self.tr("Ready"))

        # Project dock
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        dock = dock_widget.Project(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        self.view_menu.addAction(dock.toggleViewAction())

        # Object dock. Empty by default.
        # Its widget is set dynamically in runtime
        # depending on the currently selected object in the project tree.
        self.object_dock = dock_widget.Object(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.object_dock)
        self.view_menu.addAction(self.object_dock.toggleViewAction())

        # Console output dock and respective its widget
        dock = dock_widget.Console(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.view_menu.addAction(dock.toggleViewAction())

    def setup_menubar(self):
        self._setup_menubar_file()
        self._setup_menubar_help()

    def _setup_menubar_file(self):
        self.file_menu.addAction(self._settings_action())
        self.file_menu.addAction(self._quit_action())

    def _setup_menubar_help(self):
        self.help_menu.addAction(self._about_action())

    def _settings_action(self) -> QAction:
        action = QAction(self.tr("Settings..."), self)
        action.setMenuRole(QAction.PreferencesRole)
        action.triggered.connect(Settings(self, self.settings).show)  # Setting dialog is actually created here.
        return action

    def _quit_action(self) -> QAction:
        action = QAction(self.tr("Quit"), self)
        action.setMenuRole(QAction.QuitRole)
        action.setShortcut(QKeySequence.Quit)
        action.triggered.connect(self.quit_app)
        return action

    def _about_action(self) -> QAction:
        action = QAction(self.tr("About"), self)
        action.setMenuRole(QAction.AboutRole)
        action.triggered.connect(About(self).show)
        return action

    def _save_settings(self):
        """Save parameters of main window to settings."""
        self.settings.set("main_window/pos", [self.pos().x(), self.pos().y()])
        self.settings.set("main_window/size", [self.size().width(), self.size().height()])

    def _restore_settings(self):
        """Read parameters of main window from settings and apply them."""
        geometry = self.screen().availableGeometry()
        pos = self.settings.get("main_window/pos", [geometry.width() * 0.125, geometry.height() * 0.125])
        size = self.settings.get("main_window/size", [geometry.width() * 0.75, geometry.height() * 0.75])
        self.setGeometry(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))

    @Slot()
    def quit_app(self, *args, **kwargs):
        self._save_settings()
        self.app.quit()

    def closeEvent(self, *args, **kwargs):
        self._save_settings()
