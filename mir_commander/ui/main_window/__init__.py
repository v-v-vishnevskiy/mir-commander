from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMdiArea

from mir_commander import __version__
from mir_commander.projects.base import Project
from mir_commander.ui.main_window.widgets import About
from mir_commander.ui.main_window.widgets import Settings as SettingsWidget
from mir_commander.ui.main_window.widgets import dock_widget
from mir_commander.ui.utils.widget import Translator

if TYPE_CHECKING:
    from mir_commander.ui.application import Application


class MainWindow(Translator, QMainWindow):
    """The class of the main window.

    It must inherit Translator since in the main window we have
    UI elements, which may be translated on the fly.
    For this, a retranslate_ui method must be implemented!
    """

    def __init__(self, app: "Application", project: Project):
        super().__init__(None)
        self.app = app
        self.project = project

        self.project.settings.add_apply_callback("name", self._set_window_title)

        self._config = self.project.config.nested("widgets.main_window")

        self.setWindowIcon(QIcon(":/icons/general/app.svg"))

        # Mdi area as a central widget
        self.mdi_area = QMdiArea(self)
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdi_area)

        # Settings
        self._restore_settings()

        # Menu Bar
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu("File")
        self.view_menu = self.menubar.addMenu("View")
        self.help_menu = self.menubar.addMenu("Help")
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
        self.console = dock_widget.Console(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console)
        self.view_menu.addAction(self.console.toggleViewAction())

        self.console.append(self.tr("Started") + f" Mir Commander {__version__}")

        self.retranslate_ui()
        self._set_window_title()

    def _set_window_title(self):
        self.setWindowTitle(f"Mir Commander – {self.project.name}")

    def setup_menubar(self):
        self._setup_menubar_file()
        self._setup_menubar_help()

    def _setup_menubar_file(self):
        self.file_menu.addAction(self._close_project_action())
        self.file_menu.addAction(self._settings_action())
        self.file_menu.addAction(self._quit_action())

    def _setup_menubar_help(self):
        self.help_menu.addAction(self._about_action())

    def _close_project_action(self, checked: bool = False):
        action = QAction("Close Project", self)
        action.triggered.connect(self.close)
        self.close_project_action = action
        return action

    def _settings_action(self) -> QAction:
        action = QAction("Settings", self)
        action.setMenuRole(QAction.PreferencesRole)
        # Settings dialog is actually created here.
        action.triggered.connect(SettingsWidget(self).show)
        self.settings_action = action
        return action

    def _quit_action(self) -> QAction:
        action = QAction("Quit", self)
        action.setMenuRole(QAction.QuitRole)
        action.setShortcut(QKeySequence.Quit)
        action.triggered.connect(self.app.quit)
        self.quit_action = action
        return action

    def _about_action(self) -> QAction:
        action = QAction("About", self)
        action.setMenuRole(QAction.AboutRole)
        action.triggered.connect(About(self).show)
        self.about_action = action
        return action

    def _save_settings(self):
        """Save parameters of main window to settings."""
        self._config["pos"] = [self.pos().x(), self.pos().y()]
        self._config["size"] = [self.size().width(), self.size().height()]

    def _restore_settings(self):
        """Read parameters of main window from settings and apply them."""
        geometry = self.screen().availableGeometry()
        pos = self._config["pos"] or [geometry.width() * 0.125, geometry.height() * 0.125]
        size = self._config["size"] or [geometry.width() * 0.75, geometry.height() * 0.75]
        self.setGeometry(pos[0], pos[1], size[0], size[1])

    def retranslate_ui(self):
        # menubar
        self.file_menu.setTitle(self.tr("File"))
        self.view_menu.setTitle(self.tr("View"))
        self.help_menu.setTitle(self.tr("Help"))

        # actions
        self.close_project_action.setText(self.tr("Close Project"))
        self.quit_action.setText(self.tr("Quit"))
        self.settings_action.setText(self.tr("Settings..."))
        self.about_action.setText(self.tr("About"))

    def closeEvent(self, event: QCloseEvent):
        self._save_settings()
        self.app.close_project(self)
        event.accept()
