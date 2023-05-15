from dataclasses import dataclass
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon, QKeySequence
from PySide6.QtWidgets import QMainWindow, QMdiArea, QTabWidget

from mir_commander import __version__
from mir_commander.projects.base import Project
from mir_commander.ui.main_window.widgets import About
from mir_commander.ui.main_window.widgets import Settings as SettingsWidget
from mir_commander.ui.main_window.widgets import dock_widget
from mir_commander.ui.utils.widget import Action, Menu, StatusBar

if TYPE_CHECKING:
    from mir_commander.ui.application import Application


@dataclass
class DockWidgets:
    project: dock_widget.Project
    object: dock_widget.Object
    console: dock_widget.Console


class MainWindow(QMainWindow):
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

        self.setup_docks()
        self.setup_menubar()

        # Status Bar
        self.status = StatusBar(self)
        self.setStatusBar(self.status)

        self._set_window_title()

        # Settings
        self._restore_settings()

        self.status.showMessage(StatusBar.tr("Ready"), 10000)
        self.docks.console.append(self.tr("Started") + f" Mir Commander {__version__}")

    def setup_docks(self):
        self.setTabPosition(Qt.BottomDockWidgetArea, QTabWidget.TabPosition.North)
        self.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.TabPosition.West)
        self.setTabPosition(Qt.RightDockWidgetArea, QTabWidget.TabPosition.East)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)

        self.docks = DockWidgets(
            dock_widget.Project(self, self.project.config.nested("widgets.docks.project")),
            dock_widget.Object(self, self.project.config.nested("widgets.docks.object")),
            dock_widget.Console(self, self.project.config.nested("widgets.docks.console")),
        )
        self.docks.project.set_model(self.project.model)

    def _set_window_title(self):
        self.setWindowTitle(f"Mir Commander – {self.project.name}")

    def setup_menubar(self):
        menubar = self.menuBar()
        menubar.addMenu(self._setup_menubar_file())
        menubar.addMenu(self._setup_menubar_view())
        menubar.addMenu(self._setup_menubar_help())

    def _setup_menubar_file(self) -> Menu:
        menu = Menu(Menu.tr("File"), self)
        menu.addAction(self._close_project_action())
        menu.addAction(self._settings_action())
        menu.addAction(self._quit_action())
        return menu

    def _setup_menubar_view(self) -> Menu:
        menu = Menu(Menu.tr("View"), self)
        menu.addAction(self.docks.project.toggleViewAction())
        menu.addAction(self.docks.object.toggleViewAction())
        menu.addAction(self.docks.console.toggleViewAction())
        return menu

    def _setup_menubar_help(self) -> Menu:
        menu = Menu(Menu.tr("Help"), self)
        menu.addAction(self._about_action())
        return menu

    def _close_project_action(self, checked: bool = False) -> Action:
        action = Action(Action.tr("Close Project"), self)
        action.triggered.connect(self.close)
        return action

    def _settings_action(self) -> Action:
        action = Action(Action.tr("Settings..."), self)
        action.setMenuRole(Action.PreferencesRole)
        # Settings dialog is actually created here.
        action.triggered.connect(SettingsWidget(self).show)
        return action

    def _quit_action(self) -> Action:
        action = Action(Action.tr("Quit"), self)
        action.setMenuRole(Action.QuitRole)
        action.setShortcut(QKeySequence.Quit)
        action.triggered.connect(self.app.quit)
        return action

    def _about_action(self) -> Action:
        action = Action(Action.tr("About"), self)
        action.setMenuRole(Action.AboutRole)
        action.triggered.connect(About(self).show)
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

    def closeEvent(self, event: QCloseEvent):
        self._save_settings()
        self.app.close_project(self)
        event.accept()
