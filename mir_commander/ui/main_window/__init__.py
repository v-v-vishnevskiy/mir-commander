import base64
import logging
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
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


logger = logging.getLogger()


@dataclass
class DockWidgets:
    project: dock_widget.Project
    object: dock_widget.Object
    console: dock_widget.Console


class MainWindow(QMainWindow):
    def __init__(self, app: "Application", project: Project):
        super().__init__(None)
        self.app: "Application" = app
        self.project = project

        self.project.settings.add_apply_callback("name", self._set_mainwindow_title)

        self._config = self.project.config.nested("widgets.main_window")

        self.setWindowIcon(QIcon(":/icons/general/app.svg"))

        # Mdi area as a central widget
        self.mdi_area = QMdiArea(self)
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.subWindowActivated.connect(self.update_menus)
        self.setCentralWidget(self.mdi_area)

        self.setup_docks()
        self.setup_menubar()

        # Status Bar
        self.status = StatusBar(self)
        self.setStatusBar(self.status)

        self._set_mainwindow_title()

        # Settings
        self._restore_settings()

        self.status.showMessage(StatusBar.tr("Ready"), 10000)
        self.docks.console.append(self.tr("Started") + f" Mir Commander {__version__}")

        self.view_opened_items()

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
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks.project)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks.object)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.docks.console)
        self.docks.project.set_model(self.project.model)

    def _set_mainwindow_title(self):
        self.setWindowTitle(f"Mir Commander – {self.project.name}")

    def setup_menubar(self):
        menubar = self.menuBar()
        menubar.addMenu(self._setup_menubar_file())
        menubar.addMenu(self._setup_menubar_view())
        menubar.addMenu(self._setup_menubar_window())
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

    def _setup_menubar_window(self) -> Menu:
        self._window_actions()
        self._window_menu = Menu(Menu.tr("&Window"), self)
        self.update_window_menu()
        self._window_menu.aboutToShow.connect(self.update_window_menu)
        return self._window_menu

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

    def _window_actions(self):
        self._win_close_act = Action(
            Action.tr("Cl&ose"),
            self,
            statusTip=self.tr("Close the active window"),
            triggered=self.mdi_area.closeActiveSubWindow,
        )

        self._win_close_all_act = Action(
            Action.tr("Close &All"),
            self,
            statusTip=self.tr("Close all the windows"),
            triggered=self.mdi_area.closeAllSubWindows,
        )

        self._win_tile_act = Action(
            Action.tr("&Tile"), self, statusTip=self.tr("Tile the windows"), triggered=self.mdi_area.tileSubWindows
        )

        self._win_cascade_act = Action(
            Action.tr("&Cascade"),
            self,
            statusTip=self.tr("Cascade the windows"),
            triggered=self.mdi_area.cascadeSubWindows,
        )

        self._win_next_act = Action(
            Action.tr("Ne&xt"),
            self,
            shortcut=QKeySequence.NextChild,
            statusTip=self.tr("Move the focus to the next window"),
            triggered=self.mdi_area.activateNextSubWindow,
        )

        self._win_previous_act = Action(
            Action.tr("Pre&vious"),
            self,
            shortcut=QKeySequence.PreviousChild,
            statusTip=self.tr("Move the focus to the previous window"),
            triggered=self.mdi_area.activatePreviousSubWindow,
        )

        self._win_separator_act = Action(self)
        self._win_separator_act.setSeparator(True)

    def view_opened_items(self):
        for item in self.project.opened_items:
            if viewer := item.viewer():
                self.mdi_area.addSubWindow(viewer)
            else:
                logger.warning(f"No viewer for `{item.__class__.__name__}` item")

    def _save_settings(self):
        """Save parameters of main window to settings."""
        self._config["state"] = self.saveState().toBase64().toStdString()
        self._config["pos"] = [self.pos().x(), self.pos().y()]
        self._config["size"] = [self.size().width(), self.size().height()]

    def _restore_settings(self):
        """Read parameters of main window from settings and apply them."""
        geometry = self.screen().availableGeometry()
        pos = self._config["pos"] or [geometry.width() * 0.125, geometry.height() * 0.125]
        size = self._config["size"] or [geometry.width() * 0.75, geometry.height() * 0.75]
        self.setGeometry(pos[0], pos[1], size[0], size[1])
        if state := self._config["state"]:
            self.restoreState(base64.b64decode(state))

    def closeEvent(self, event: QCloseEvent):
        self._save_settings()
        self.app.close_project(self)
        event.accept()

    def active_mdi_child(self):
        active_sub_window = self.mdi_area.activeSubWindow()
        if active_sub_window:
            return active_sub_window.widget()
        return None

    @Slot()
    def update_menus(self):
        has_mdi_child = self.active_mdi_child() is not None
        self._win_close_act.setEnabled(has_mdi_child)
        self._win_close_all_act.setEnabled(has_mdi_child)
        self._win_tile_act.setEnabled(has_mdi_child)
        self._win_cascade_act.setEnabled(has_mdi_child)
        self._win_next_act.setEnabled(has_mdi_child)
        self._win_previous_act.setEnabled(has_mdi_child)
        self._win_separator_act.setVisible(has_mdi_child)

    def set_active_sub_window(self, window):
        if window:
            self.mdi_area.setActiveSubWindow(window)

    @Slot()
    def update_window_menu(self):
        self._window_menu.clear()
        self._window_menu.addAction(self._win_close_act)
        self._window_menu.addAction(self._win_close_all_act)
        self._window_menu.addSeparator()
        self._window_menu.addAction(self._win_tile_act)
        self._window_menu.addAction(self._win_cascade_act)
        self._window_menu.addSeparator()
        self._window_menu.addAction(self._win_next_act)
        self._window_menu.addAction(self._win_previous_act)
        self._window_menu.addAction(self._win_separator_act)

        windows = self.mdi_area.subWindowList()
        self._win_separator_act.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child = window.widget()

            f = window.windowTitle()
            text = f"{i + 1} {f}"
            if i < 9:
                text = "&" + text

            action = self._window_menu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.active_mdi_child())
            slot_func = partial(self.set_active_sub_window, window=window)
            action.triggered.connect(slot_func)
