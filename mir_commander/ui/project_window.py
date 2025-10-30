import base64
import logging
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QCloseEvent, QIcon, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMdiSubWindow, QTabWidget

from mir_commander import __version__
from mir_commander.core import Project
from mir_commander.core.project_node import ProjectNode
from mir_commander.plugin_system.file_exporter import ExportFileError
from mir_commander.plugin_system.file_importer import ImportFileError

from .config import AppConfig, ApplyCallbacks
from .mdi_area import MdiArea
from .utils.program import ProgramControlPanel, ProgramWindow
from .utils.widget import Action, Dialog, Menu, StatusBar
from .widgets.about import About
from .widgets.docks.console_dock import ConsoleDock
from .widgets.docks.project_dock.items import TreeItem
from .widgets.docks.project_dock.project_dock import ProjectDock
from .widgets.export_item_dialog import ExportFileDialog
from .widgets.settings.settings_dialog import SettingsDialog

logger = logging.getLogger("ProjectWindow")


@dataclass
class Docks:
    project: ProjectDock
    console: ConsoleDock


class ProjectWindow(QMainWindow):
    close_project_signal = Signal(QMainWindow)
    quit_application_signal = Signal()

    def __init__(
        self,
        app_config: AppConfig,
        app_apply_callbacks: ApplyCallbacks,
        project: Project,
        init_msg: None | list[str] = None,
    ):
        logger.debug("Initializing main window ...")
        super().__init__(None)

        self._programs_control_panels: dict[type[ProgramControlPanel], ProgramControlPanel] = {}

        self.project = project
        self.app_config = app_config
        self.config = app_config.project_window
        self.app_apply_callbacks = app_apply_callbacks
        self.apply_callbacks = ApplyCallbacks()

        self.apply_callbacks.add(self._set_mainwindow_title)

        self.setWindowIcon(QIcon(":/icons/general/app.svg"))

        self.setup_docks()  # Create docks before menus
        self.setup_mdi_area()
        self.setup_menubar()  # Toolbars and docks must have been already created, so we can populate the View menu.

        # Status Bar
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)

        self._set_mainwindow_title()

        self.mdi_area.tileSubWindows()

        # Settings
        self._restore_settings()

        self.update_menus(None)

        self.append_to_console(self.tr("Started {name} {version}").format(name="Mir Commander", version=__version__))
        if init_msg:
            for msg in init_msg:
                self.append_to_console(msg)

        self.status_bar.showMessage(StatusBar.tr("Ready"), 10000)

        if project.is_temporary:
            self.docks.project.tree.expand_top_items()
            self.docks.project.tree.view_babushka()

    @property
    def programs_control_panels(self) -> dict[type[ProgramControlPanel], ProgramControlPanel]:
        return self._programs_control_panels

    def append_to_console(self, text: str):
        self.docks.console.append(text)

    def setup_mdi_area(self):
        def opened_program_slot(program: ProgramWindow):
            program.short_msg_signal.connect(self.status_bar.showMessage)
            program.long_msg_signal.connect(self.docks.console.append)

        self.mdi_area = MdiArea(self, app_config=self.app_config, parent=self)
        self.mdi_area.subWindowActivated.connect(self.update_menus)
        self.mdi_area.opened_program_signal.connect(opened_program_slot)
        self.setCentralWidget(self.mdi_area)

        self.docks.project.tree.view_item.connect(self.mdi_area.open_program)

    def setup_docks(self):
        self.setTabPosition(Qt.DockWidgetArea.BottomDockWidgetArea, QTabWidget.TabPosition.North)
        self.setTabPosition(Qt.DockWidgetArea.LeftDockWidgetArea, QTabWidget.TabPosition.West)
        self.setTabPosition(Qt.DockWidgetArea.RightDockWidgetArea, QTabWidget.TabPosition.East)
        self.setCorner(Qt.Corner.BottomLeftCorner, Qt.DockWidgetArea.LeftDockWidgetArea)
        self.setCorner(Qt.Corner.BottomRightCorner, Qt.DockWidgetArea.RightDockWidgetArea)

        self.docks = Docks(
            ProjectDock(
                parent=self,
                config=self.config.widgets.docks.project,
                project=self.project,
            ),
            ConsoleDock(parent=self),
        )
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.docks.project)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.docks.console)

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
        menu.addAction(self._import_file_action())
        menu.addSeparator()
        menu.addAction(self._settings_action())
        menu.addAction(self._close_project_action())
        menu.addAction(self._quit_action())
        return menu

    def _setup_menubar_view(self) -> Menu:
        self._view_menu = Menu(Menu.tr("View"), self)
        self._view_menu.addAction(self.docks.project.toggleViewAction())
        self._view_menu.addAction(self.docks.console.toggleViewAction())
        return self._view_menu

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
        action.setMenuRole(Action.MenuRole.PreferencesRole)
        # Settings dialog is actually created here.
        settings_dialog = SettingsDialog(
            parent=self,
            app_apply_callbacks=self.app_apply_callbacks,
            mw_apply_callbacks=self.apply_callbacks,
            app_config=self.app_config,
            project_config=self.project.config,
        )
        action.triggered.connect(settings_dialog.show)
        return action

    def _quit_action(self) -> Action:
        action = Action(Action.tr("Quit"), self)
        action.setMenuRole(Action.MenuRole.QuitRole)
        action.setShortcut(QKeySequence.StandardKey.Quit)
        action.triggered.connect(self.quit_application_signal.emit)
        return action

    def _about_action(self) -> Action:
        action = Action(Action.tr("About"), self)
        action.setMenuRole(Action.MenuRole.AboutRole)
        action.triggered.connect(About(self).show)
        return action

    def _import_file_action(self) -> Action:
        action = Action(Action.tr("Import File..."), self)
        action.setShortcut(QKeySequence(self.config.hotkeys.menu_file.import_file))
        action.triggered.connect(self.import_file)
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
            shortcut=QKeySequence.StandardKey.NextChild,
            statusTip=self.tr("Move the focus to the next window"),
            triggered=self.mdi_area.activateNextSubWindow,
        )

        self._win_previous_act = Action(
            Action.tr("Pre&vious"),
            self,
            shortcut=QKeySequence.StandardKey.PreviousChild,
            statusTip=self.tr("Move the focus to the previous window"),
            triggered=self.mdi_area.activatePreviousSubWindow,
        )

        self._win_separator_act = Action("", self)
        self._win_separator_act.setSeparator(True)

    def _save_settings(self):
        """Save parameters of main window to settings."""
        self.config.state = self.saveState().toBase64().toStdString()
        self.config.pos = [self.pos().x(), self.pos().y()]
        self.config.size = [self.size().width(), self.size().height()]

    def _restore_settings(self):
        """Read parameters of main window from settings and apply them."""
        geometry = self.screen().availableGeometry()
        pos = self.config.pos or [int(geometry.width() * 0.125), int(geometry.height() * 0.125)]
        size = self.config.size or [int(geometry.width() * 0.75), int(geometry.height() * 0.75)]
        self.setGeometry(pos[0], pos[1], size[0], size[1])
        if state := self.config.state:
            self.restoreState(base64.b64decode(state))

    def closeEvent(self, event: QCloseEvent):
        logger.info("Closing %s project ...", self.project.name)
        self._save_settings()
        self.close_project_signal.emit(self)
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

    def set_active_sub_window(self, window: QMdiSubWindow) -> None:
        if window:
            self.mdi_area.setActiveSubWindow(window)

    def add_program_control_panel(self, control_panel_cls: type[ProgramControlPanel]) -> ProgramControlPanel:
        if control_panel_cls not in self._programs_control_panels:
            self._programs_control_panels[control_panel_cls] = control_panel_cls(parent=self)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self._programs_control_panels[control_panel_cls])
            self._view_menu.addAction(self._programs_control_panels[control_panel_cls].toggleViewAction())
        return self._programs_control_panels[control_panel_cls]

    def import_file(self, parent: TreeItem | None = None):
        """Import a file into the current project."""

        dialog = QFileDialog(self, self.tr("Import File"))
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter(self.tr("All files (*)"))

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = Path(dialog.selectedFiles()[0])
            try:
                logs: list[str] = []
                imported_item = self.project.import_file(
                    file_path, logs, parent.project_node if parent is not None else None
                )
                self.docks.project.tree._add_item(imported_item, parent)

                # Show import messages in console
                self.append_to_console(f"Imported file: {file_path}")
                for log in logs:
                    self.append_to_console(log)

                self.status_bar.showMessage(self.tr("File imported successfully"), 3000)
            except ImportFileError as e:
                logger.error("Failed to import file %s: %s", file_path, e)
                self.append_to_console(
                    self.tr("Error importing file {file_path}: {e}").format(file_path=file_path, e=e)
                )
                self.status_bar.showMessage(self.tr("Failed to import file"), 5000)

    def export_file(self, node: ProjectNode):
        dialog = ExportFileDialog(node, parent=self)

        if dialog.exec() == Dialog.DialogCode.Accepted:
            path, exporter_name, format_settings = dialog.get_params()
            try:
                self.project.export_file(
                    node=node,
                    exporter_name=exporter_name,
                    path=path,
                    format_settings=format_settings,
                )
                self.status_bar.showMessage(self.tr("File exported successfully"), 3000)
            except ExportFileError as e:
                logger.error("Failed to export file: %s", e)
                self.append_to_console(self.tr("Failed to export file: {}").format(e))
                self.status_bar.showMessage(self.tr("Failed to export file"), 5000)

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
