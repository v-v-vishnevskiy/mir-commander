import base64
import logging
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from PySide6.QtCore import QCoreApplication, Qt, Signal, Slot
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence
from PySide6.QtWidgets import QDialog, QFileDialog, QMainWindow, QMdiSubWindow, QMenu, QStatusBar, QTabWidget

from mir_commander import __version__
from mir_commander.api.file_exporter import ExportFileError
from mir_commander.api.file_importer import ImportFileError
from mir_commander.api.program import MessageChannel, UINode
from mir_commander.core import Project, plugins_registry
from mir_commander.core.file_manager import FileManager
from mir_commander.core.project_node import ProjectNode

from .about import About
from .config import AppConfig, ApplyCallbacks
from .docks.console_dock import ConsoleDock
from .docks.program_control_panel import ProgramControlPanelDock
from .docks.project_dock.project_dock import ProjectDock
from .export_item_dialog import ExportFileDialog
from .mdi_area import MdiArea
from .settings.settings_dialog import SettingsDialog

logger = logging.getLogger("UI.ProjectWindow")


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

        self._programs_control_panels: dict[str, ProgramControlPanelDock] = {}

        self.project = project
        self.app_config = app_config
        self.config = app_config.project_window
        self.app_apply_callbacks = app_apply_callbacks
        self.apply_callbacks = ApplyCallbacks()

        self.apply_callbacks.add(self._set_mainwindow_title)

        self._file_manager = FileManager(plugins_registry)

        self.setWindowIcon(QIcon(":/core/icons/app.svg"))

        self.setup_docks()  # Create docks before menus
        self.setup_mdi_area()
        self.setup_menubar()  # Toolbars and docks must have been already created, so we can populate the View menu.

        # Status Bar
        self.status_bar = QStatusBar(self)
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

        self.status_bar.showMessage(self.tr("Ready"), 10000)

        if project.is_temporary:
            self.docks.project.tree.expand_top_items()
            self.docks.project.tree.open_auto_open_nodes(self.app_config.import_file_rules, True)

    @property
    def programs_control_panels(self) -> dict[str, ProgramControlPanelDock]:
        return self._programs_control_panels

    def append_to_console(self, text: str):
        self.docks.console.append(text)

    def setup_mdi_area(self):
        def program_send_message_handler(message_channel: MessageChannel, message: str):
            if message_channel == MessageChannel.CONSOLE:
                self.append_to_console(message)
            elif message_channel == MessageChannel.STATUS:
                self.status_bar.showMessage(message, 10000)
            else:
                logger.error("Unknown message channel: %s", message_channel)

        self.mdi_area = MdiArea(project_window=self, parent=self)
        self.mdi_area.subWindowActivated.connect(self.update_menus)
        self.mdi_area.program_send_message_signal.connect(program_send_message_handler)
        self.setCentralWidget(self.mdi_area)

        self.docks.project.tree.open_item.connect(self.mdi_area.open_program)

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
        self.setWindowTitle(self.project.name)

    def setup_menubar(self):
        menubar = self.menuBar()
        menubar.addMenu(self._setup_menubar_file())
        menubar.addMenu(self._setup_menubar_view())
        menubar.addMenu(self._setup_menubar_window())
        menubar.addMenu(self._setup_menubar_help())

    def _setup_menubar_file(self) -> QMenu:
        menu = QMenu(self.tr("File"), self)
        menu.addAction(self._import_file_action())
        menu.addSeparator()
        menu.addAction(self._settings_action())
        menu.addAction(self._close_project_action())
        menu.addAction(self._quit_action())
        return menu

    def _setup_menubar_view(self) -> QMenu:
        self._view_menu = QMenu(self.tr("View"), self)
        self._view_menu.addAction(self.docks.project.toggleViewAction())
        self._view_menu.addAction(self.docks.console.toggleViewAction())
        return self._view_menu

    def _setup_menubar_window(self) -> QMenu:
        self._window_actions()
        self._window_menu = QMenu(self.tr("Window"), self)
        self.update_window_menu()
        self._window_menu.aboutToShow.connect(self.update_window_menu)
        return self._window_menu

    def _setup_menubar_help(self) -> QMenu:
        menu = QMenu(self.tr("Help"), self)
        menu.addAction(self._about_action())
        return menu

    def _close_project_action(self, checked: bool = False) -> QAction:
        action = QAction(self.tr("Close Project"), self)
        action.triggered.connect(self.close)
        return action

    def _settings_action(self) -> QAction:
        action = QAction(self.tr("Settings..."), self)
        action.setMenuRole(QAction.MenuRole.PreferencesRole)
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

    def _quit_action(self) -> QAction:
        action = QAction(self.tr("Quit"), self)
        action.setMenuRole(QAction.MenuRole.QuitRole)
        action.setShortcut(QKeySequence.StandardKey.Quit)
        action.triggered.connect(self.quit_application_signal.emit)
        return action

    def _about_action(self) -> QAction:
        action = QAction(self.tr("About"), self)
        action.setMenuRole(QAction.MenuRole.AboutRole)
        action.triggered.connect(About(self).show)
        return action

    def _import_file_action(self) -> QAction:
        action = QAction(self.tr("Import File..."), self)
        action.setShortcut(QKeySequence(self.config.hotkeys.menu_file.import_file))
        action.triggered.connect(self.import_file)
        return action

    def _window_actions(self):
        self._win_close_act = QAction(text=self.tr("Close"), parent=self, statusTip=self.tr("Close the active window"))
        self._win_close_act.triggered.connect(self.mdi_area.closeActiveSubWindow)

        self._win_close_all_act = QAction(
            text=self.tr("Close All"), parent=self, statusTip=self.tr("Close all the windows")
        )
        self._win_close_all_act.triggered.connect(self.mdi_area.closeAllSubWindows)

        self._win_tile_act = QAction(text=self.tr("Tile"), parent=self, statusTip=self.tr("Tile the windows"))
        self._win_tile_act.triggered.connect(self.mdi_area.tileSubWindows)

        self._win_cascade_act = QAction(text=self.tr("Cascade"), parent=self, statusTip=self.tr("Cascade the windows"))
        self._win_cascade_act.triggered.connect(self.mdi_area.cascadeSubWindows)

        self._win_next_act = QAction(
            text=self.tr("Next"),
            parent=self,
            shortcut=QKeySequence(QKeySequence.StandardKey.NextChild),
            statusTip=self.tr("Move the focus to the next window"),
        )
        self._win_next_act.triggered.connect(self.mdi_area.activateNextSubWindow)

        self._win_previous_act = QAction(
            text=self.tr("Previous"),
            parent=self,
            shortcut=QKeySequence(QKeySequence.StandardKey.PreviousChild),
            statusTip=self.tr("Move the focus to the previous window"),
        )
        self._win_previous_act.triggered.connect(self.mdi_area.activatePreviousSubWindow)

        self._win_separator_act = QAction("", self)
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

    def add_program_control_panel(self, program_id: str) -> None | ProgramControlPanelDock:
        if program_id not in self._programs_control_panels:
            program = plugins_registry.program.get(program_id)
            control_panel_cls = program.details.control_panel_class
            if control_panel_cls is None:
                return None
            control_panel = control_panel_cls()
            program_control_panel_dock = ProgramControlPanelDock(
                program_id=program_id, control_panel=control_panel, parent=self
            )
            program_control_panel_dock.setWindowTitle(QCoreApplication.translate(program_id, program.metadata.name))
            control_panel.program_action_signal.connect(
                lambda key, data: self.mdi_area.update_program_event(
                    program_id, program_control_panel_dock.apply_for_all, key, data
                )
            )
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, program_control_panel_dock)
            self._view_menu.addAction(program_control_panel_dock.toggleViewAction())
            self._programs_control_panels[program_id] = program_control_panel_dock
        return self._programs_control_panels[program_id]

    def import_file(self, parent: UINode | None = None):
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
                self.docks.project.add_node(imported_item, parent)

                # Show import messages in console
                self.append_to_console(f"Imported file: {file_path}")
                for log in logs:
                    self.append_to_console(log)

                self.status_bar.showMessage(self.tr("File imported successfully"), 3000)
                self.docks.project.tree.open_auto_open_nodes(self.app_config.import_file_rules, False)
            except ImportFileError as e:
                logger.error("Failed to import file %s: %s", file_path, e)
                self.append_to_console(
                    self.tr("Error importing file {file_path}: {e}").format(file_path=file_path, e=e)
                )
                self.status_bar.showMessage(self.tr("Failed to import file"), 5000)

    def export_file(self, node: ProjectNode):
        dialog = ExportFileDialog(node, file_manager=self._file_manager, parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            path, exporter_id, format_settings = dialog.get_params()
            try:
                self._file_manager.export_file(
                    node=node, exporter_id=exporter_id, path=path, format_params=format_settings
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
