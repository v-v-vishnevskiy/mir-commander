import base64
import logging
from dataclasses import dataclass
from functools import partial
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent, QIcon, QKeySequence
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMainWindow, QMdiArea, QMdiSubWindow, QTabWidget

from mir_commander import __version__
from mir_commander.projects.base import Project
from mir_commander.ui.main_window.widgets import About
from mir_commander.ui.main_window.widgets import Settings as SettingsWidget
from mir_commander.ui.main_window.widgets import dock_widget
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.menu import Menu as MolStructMenu
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.toolbar import ToolBar as MolStructToolBar
from mir_commander.ui.utils.widget import Action, Menu, StatusBar

if TYPE_CHECKING:
    from mir_commander.ui.application import Application
    from mir_commander.ui.utils.sub_window_menu import SubWindowMenu
    from mir_commander.ui.utils.sub_window_toolbar import SubWindowToolBar


logger = logging.getLogger()


@dataclass
class DockWidgets:
    project: dock_widget.Project
    object: dock_widget.Object
    console: dock_widget.Console


class MainWindow(QMainWindow):
    def __init__(self, app: "Application", project: Project, init_msg: None | list[str] = None):
        super().__init__(None)
        self.app: "Application" = app
        self.project = project
        self.sub_window_menus: list[SubWindowMenu] = []  # Menus of SubWindows
        self.sub_window_toolbars: list[SubWindowToolBar] = []  # Toolbars of SubWindows

        self.project.settings.add_apply_callback("name", self._set_mainwindow_title)

        self._config = self.project.config.nested("widgets.main_window")

        self.setWindowIcon(QIcon(":/icons/general/app.svg"))

        # Mdi area as a central widget
        self.mdi_area = QMdiArea(self)
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi_area.subWindowActivated.connect(self.update_menus)
        self.mdi_area.subWindowActivated.connect(self.update_toolbars)
        self.setCentralWidget(self.mdi_area)

        self.setup_toolbars()  # Note, we create toolbars before menus
        self.setup_docks()  # Create docks before menus
        self.setup_menubar()  # Toolbars and docks must have been already created, so we can populate the View menu.

        # Status Bar
        self.status = StatusBar(self)
        self.setStatusBar(self.status)

        self._set_mainwindow_title()

        # Settings
        self._restore_settings()

        self.update_menus(None)

        self.append_to_console(self.tr("Started") + f" Mir Commander {__version__}")
        if init_msg:
            for msg in init_msg:
                self.append_to_console(msg)

        self._fix_window_composition()

        self.view_items_marked_to_view()

        self.status.showMessage(StatusBar.tr("Ready"), 10000)

    def append_to_console(self, text: str):
        self.docks.console.append(text)

    def _fix_window_composition(self):
        widget = QOpenGLWidget()
        widget.item = None
        self.__fix_sub_window = self.mdi_area.addSubWindow(widget)
        self.__fix_sub_window.hide()

    def show(self):
        super().show()
        if self.__fix_sub_window:
            self.mdi_area.removeSubWindow(self.__fix_sub_window)
            self.__fix_sub_window = None

    def setup_docks(self):
        self.setTabPosition(Qt.BottomDockWidgetArea, QTabWidget.TabPosition.North)
        self.setTabPosition(Qt.LeftDockWidgetArea, QTabWidget.TabPosition.West)
        self.setTabPosition(Qt.RightDockWidgetArea, QTabWidget.TabPosition.East)
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)

        self.docks = DockWidgets(dock_widget.Project(self), dock_widget.Object(self), dock_widget.Console(self))
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docks.project)
        self.addDockWidget(Qt.RightDockWidgetArea, self.docks.object)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.docks.console)
        self.docks.project.set_model(self.project.model)
        self.docks.project.expand_items(self.project.items_marked_to_expand)

    def setup_toolbars(self):
        # N.B.: toolbar(s) of the main window will be also created in this function.

        # Here we collect classes of widgets, which create their own toolbars for the main window.
        # The logic for such toolbars is implemented inside particular classes, see MolViewer for an example.
        self.sub_window_toolbars.append(MolStructToolBar(self))

        for toolbar in self.sub_window_toolbars:
            self.addToolBar(toolbar)

    def _set_mainwindow_title(self):
        self.setWindowTitle(f"Mir Commander – {self.project.name}")

    def setup_menubar(self):
        # Collect all additional menus from viewers.
        # Here is the same logic as for toolbars of particular widgets.
        self.sub_window_menus.append(MolStructMenu(self))

        menubar = self.menuBar()
        menubar.addMenu(self._setup_menubar_file())
        menubar.addMenu(self._setup_menubar_view())
        menubar.addMenu(self._setup_menubar_window())

        for menu in self.sub_window_menus:
            menubar.addMenu(menu)

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
        menu.addSeparator()
        for toolbar in self.sub_window_toolbars:
            menu.addAction(toolbar.toggleViewAction())
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

        self._win_separator_act = Action("", self)
        self._win_separator_act.setSeparator(True)

    def view_items_marked_to_view(self):
        for config_item in self.project.items_marked_to_view:
            maximize_flag = config_item.parameters.get("maximize", False)
            item = config_item.item
            if item.view(maximize_flag) is None:
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

    @Slot()
    def update_menus(self, window: None | QMdiSubWindow):
        has_mdi_child = window is not None
        self._win_close_act.setEnabled(has_mdi_child)
        self._win_close_all_act.setEnabled(has_mdi_child)
        self._win_tile_act.setEnabled(has_mdi_child)
        self._win_cascade_act.setEnabled(has_mdi_child)
        self._win_next_act.setEnabled(has_mdi_child)
        self._win_previous_act.setEnabled(has_mdi_child)
        self._win_separator_act.setVisible(has_mdi_child)

        for menu in self.sub_window_menus:
            menu.update_state(window)

    @Slot()
    def update_toolbars(self, window: None | QMdiSubWindow):
        for toolbar in self.sub_window_toolbars:
            toolbar.update_state(window)

    def set_active_sub_window(self, window: QMdiSubWindow) -> None:
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
        active_sub_window = self.mdi_area.activeSubWindow()
        self._win_separator_act.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            f = window.windowTitle()
            text = f"{i + 1} {f}"
            if i < 9:
                text = "&" + text

            action = self._window_menu.addAction(text)
            action.setCheckable(True)
            action.setChecked(window is active_sub_window)
            slot_func = partial(self.set_active_sub_window, window=window)
            action.triggered.connect(slot_func)
