import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Protocol

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QBrush, QCloseEvent, QColor, QResizeEvent, QWindowStateChangeEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QMessageBox, QVBoxLayout, QWidget

from mir_commander.api.program import MessageChannel, NodeChangedAction, ProgramConfig, ProgramError, UINode
from mir_commander.core.errors import PluginDisabledError, PluginNotFoundError
from mir_commander.core.plugins_registry import plugins_registry
from mir_commander.ui.sdk.widget import MdiSubWindowBody, MdiSubWindowTitleBar, ResizableContainer

from .docks.program_control_panel import ProgramControlPanelDock

if TYPE_CHECKING:
    from .project_window import ProjectWindow


logger = logging.getLogger("UI.MdiArea")


class _MdiProgramWindow(QMdiSubWindow):
    _id_counter = 0

    _opened_programs = defaultdict[str, int](int)

    def __init__(
        self,
        program_id: str,
        node: UINode,
        config: ProgramConfig,
        program_control_panel_dock: None | ProgramControlPanelDock,
        parent: QWidget,
        kwargs: dict[str, Any],
    ):
        _MdiProgramWindow._id_counter += 1
        self._id = _MdiProgramWindow._id_counter

        self._program_id = program_id

        self.program = plugins_registry.program.get(program_id).details.program_class(
            node=node, config=config, **kwargs
        )
        self.program_control_panel_dock = program_control_panel_dock

        super().__init__(parent=parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._last_normal_size = QSize(0, 0)

        self._custom_title_bar = MdiSubWindowTitleBar(self)
        self._custom_title_bar.set_icon(self.program.get_icon())
        self._custom_title_bar.set_title(self.program.get_title())

        self._custom_body = MdiSubWindowBody(widget=self.program.get_widget(), parent=self)

        self._container = QWidget(self)
        self._container.setMouseTracking(True)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self._custom_title_bar)
        container_layout.addWidget(self._custom_body)

        self._resizable_container = ResizableContainer(parent=self)

        self.setWidget(self._container)
        self.setWindowTitle(self.program.get_title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(
            config.window_size.min_width, config.window_size.min_height + self._custom_title_bar.size().height()
        )
        self.resize(config.window_size.width, config.window_size.height + self._custom_title_bar.size().height())

        self.windowStateChanged.connect(self._window_state_changed_handler)

        _MdiProgramWindow._opened_programs[self._program_id] += 1
        if _MdiProgramWindow._opened_programs[self._program_id] == 1 and program_control_panel_dock is not None:
            program_control_panel_dock.restore_visibility()
            program_control_panel_dock.toggleViewAction().setVisible(True)

    def _window_state_changed_handler(self, old_state: Qt.WindowState, new_state: Qt.WindowState):
        if new_state == Qt.WindowState.WindowActive:
            self._custom_title_bar.set_active(True)
        elif new_state == Qt.WindowState.WindowNoState:
            self._custom_title_bar.set_active(False)

        if new_state & Qt.WindowState.WindowMinimized:
            self.resize(230, self._custom_title_bar.size().height())
            self._custom_body.setVisible(False)
        elif old_state & Qt.WindowState.WindowMinimized:
            self._custom_body.setVisible(True)
            self.setMinimumSize(self.program.config.window_size.min_width, self.program.config.window_size.min_height)
            self.resize(self._last_normal_size)

        self._custom_title_bar.update_state(new_state)

        if self.program_control_panel_dock is not None:
            self.program_control_panel_dock.control_panel.update_event(self.program, {})

    @property
    def id(self) -> int:
        return self._id

    @property
    def program_id(self) -> str:
        return self._program_id

    def update_title(self):
        self.setWindowTitle(self.program.get_title())
        self._custom_title_bar.set_icon(self.program.get_icon())
        self._custom_title_bar.set_title(self.program.get_title())

    def changeEvent(self, event: QEvent):
        super().changeEvent(event)
        if isinstance(event, QWindowStateChangeEvent):
            if self.isMinimized():
                # NOTE: to prevent
                # "QWidget::setMinimumSize: (/_MdiProgramWindow) Negative sizes (-1,-1) are not possible" error
                self.setMinimumSize(0, 0)

    def resizeEvent(self, event: QResizeEvent):
        self._resizable_container.resize(event.size().width(), event.size().height())
        self._custom_body.resize(event.size().width(), event.size().height() - self._custom_title_bar.size().height())
        super().resizeEvent(event)

    def closeEvent(self, event: QCloseEvent):
        if self.isMaximized():
            self.showNormal()

        _MdiProgramWindow._opened_programs[self._program_id] -= 1
        if self.program_control_panel_dock is not None and _MdiProgramWindow._opened_programs[self._program_id] == 0:
            self.program_control_panel_dock.hide()
            self.program_control_panel_dock.toggleViewAction().setVisible(False)
        super().closeEvent(event)

    def showMinimized(self):
        if not self.isMaximized():
            self._last_normal_size = self.size()
        super().showMinimized()

    def showMaximized(self):
        if not self.isMinimized():
            self._last_normal_size = self.size()
        super().showMaximized()


class SubWindowListFn(Protocol):
    def __call__(self, /, order: QMdiArea.WindowOrder = ...) -> list[_MdiProgramWindow]: ...


class MdiArea(QMdiArea):
    program_send_message_signal = Signal(MessageChannel, str)
    subWindowList: SubWindowListFn  # type: ignore[assignment]
    currentSubWindow: Callable[[], _MdiProgramWindow]

    def __init__(self, project_window: "ProjectWindow", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._project_window = project_window

        self.setViewport(QOpenGLWidget())
        self.setBackground(QBrush(QColor("#bbbbbb")))
        self.setActivationOrder(QMdiArea.WindowOrder.ActivationHistoryOrder)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def _node_changed_handler(self, node_id: int, window_id: int, action: NodeChangedAction):
        for window in self.subWindowList():
            if window.id != window_id:
                window.program.node_changed_event(node_id, action)

    def _update_control_panel_handler(self, window: _MdiProgramWindow, data: dict[Any, Any]):
        w = self.currentSubWindow()
        if window.program_control_panel_dock is not None and w is not None and w.id == window.id:
            window.program_control_panel_dock.control_panel.update_event(window.program, data)

    def _update_window_title_handler(self, title: str):
        w = self.currentSubWindow()
        if w is None:
            return

        w.update_title()

    def open_program(self, node: UINode, program_id: str, kwargs: dict[str, Any]):
        for window in self.subWindowList():
            # checking if program for this node already opened
            if window.program_id == program_id and window.program.node == node:
                self.setActiveSubWindow(window)
                window.show()
                return

        error_title = None
        error_message = None

        try:
            program_control_panel_dock = self._project_window.add_program_control_panel(program_id)
            window = _MdiProgramWindow(
                program_id=program_id,
                node=node,
                config=plugins_registry.program.get(program_id).details.config_class(),
                program_control_panel_dock=program_control_panel_dock,
                parent=self,
                kwargs=kwargs,
            )
            self.addSubWindow(window)
            window.program.node_changed_signal.connect(
                lambda node_id, action: self._node_changed_handler(node_id, window.id, action)
            )
            window.program.send_message_signal.connect(self.program_send_message_signal.emit)
            window.program.update_control_panel_signal.connect(
                lambda data: self._update_control_panel_handler(window, data)
            )
            window.program.update_window_title_signal.connect(self._update_window_title_handler)
            window.show()
        except ProgramError as e:
            logger.error("Failed to open program `%s`: %s", program_id, e)
            error_title = "Program Error"
            error_message = f"Failed to open program '{program_id}':\n{str(e)}"
        except PluginNotFoundError:
            logger.error("Program `%s` is not registered", program_id)
            error_title = "Plugin Not Found"
            error_message = f"Program '{program_id}' is not registered in the plugin registry."
        except PluginDisabledError:
            logger.error("Program `%s` is disabled", program_id)
            error_title = "Plugin Disabled"
            error_message = f"Program '{program_id}' is currently disabled."
        except Exception as e:
            logger.error("Failed to open program `%s`: %s", program_id, e)
            error_title = "Unexpected Error"
            error_message = f"Failed to open program '{program_id}':\n{str(e)}"

        if error_title and error_message:
            error_dialog = QMessageBox(self)
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setWindowTitle(error_title)
            error_dialog.setText(error_title)
            error_dialog.setInformativeText(error_message)
            error_dialog.show()

    def update_program_event(self, program_id: str, apply_for_all: bool, key: str, data: dict[str, Any]):
        i = 0
        for window in reversed(self.subWindowList(QMdiArea.WindowOrder.ActivationHistoryOrder)):
            if window.program_id == program_id:
                window.program.action_event(key, data, i)
                i += 1
                if apply_for_all is False:
                    break
