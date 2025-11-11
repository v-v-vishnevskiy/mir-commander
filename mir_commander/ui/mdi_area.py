import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMdiArea, QMdiSubWindow, QWidget

from mir_commander.api.program import MessageChannel, NodeChangedAction, ProgramConfig, UINode
from mir_commander.core import plugins_registry
from mir_commander.core.errors import PluginNotFoundError

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
        super().__init__(parent=parent)

        _MdiProgramWindow._id_counter += 1
        self._id = _MdiProgramWindow._id_counter

        self._program_id = program_id

        self.program = plugins_registry.program.get(program_id).details.program_class(
            node=node, config=config, **kwargs
        )
        self.program_control_panel_dock = program_control_panel_dock

        self.setWidget(self.program.get_widget())
        self.setWindowIcon(self.program.get_icon())
        self.setWindowTitle(self.program.get_title())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setMinimumSize(config.window_size.min_width, config.window_size.min_height)
        self.resize(config.window_size.width, config.window_size.height)

        _MdiProgramWindow._opened_programs[self._program_id] += 1
        if self.program_control_panel_dock is not None and _MdiProgramWindow._opened_programs[self._program_id] == 1:
            self.program_control_panel_dock.restore_visibility()
            self.program_control_panel_dock.toggleViewAction().setVisible(True)

    @property
    def id(self) -> int:
        return self._id

    @property
    def program_id(self) -> str:
        return self._program_id

    def update_title(self):
        self.setWindowIcon(self.program.get_icon())
        self.setWindowTitle(self.program.get_title())

    def closeEvent(self, event: QCloseEvent):
        _MdiProgramWindow._opened_programs[self._program_id] -= 1
        if self.program_control_panel_dock is not None and _MdiProgramWindow._opened_programs[self._program_id] == 0:
            self.program_control_panel_dock.hide()
            self.program_control_panel_dock.toggleViewAction().setVisible(False)
        super().closeEvent(event)


class MdiArea(QMdiArea):
    program_send_message_signal = Signal(MessageChannel, str)

    def __init__(self, project_window: "ProjectWindow", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._project_window = project_window

        self.setActivationOrder(QMdiArea.WindowOrder.ActivationHistoryOrder)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.subWindowActivated.connect(self._sub_window_activated_handler)

    def _sub_window_activated_handler(self, window: None | _MdiProgramWindow):
        if window is None:
            return

        if window.program_control_panel_dock is not None:
            window.program_control_panel_dock.control_panel.update_event(window.program)

    def _node_changed_handler(self, node_id: int, window_id: int, action: NodeChangedAction):
        for window in cast(list[_MdiProgramWindow], self.subWindowList()):
            if window.id != window_id:
                window.program.node_changed_event(node_id, action)

    def _update_control_panel_handler(self):
        w = self.currentSubWindow()
        if w is None:
            return

        window = cast(_MdiProgramWindow, w)
        if window.program_control_panel_dock is not None:
            window.program_control_panel_dock.control_panel.update_event(window.program)

    def _update_window_title_handler(self, title: str):
        w = self.currentSubWindow()
        if w is None:
            return

        cast(_MdiProgramWindow, w).update_title()

    def open_program(self, node: UINode, program_id: str, kwargs: dict[str, Any]):
        for window in cast(list[_MdiProgramWindow], self.subWindowList()):
            # checking if program for this node already opened
            if window.program_id == program_id and window.program.node == node:
                self.setActiveSubWindow(window)
                window.show()
                return

        try:
            window = _MdiProgramWindow(
                program_id=program_id,
                node=node,
                config=plugins_registry.program.get(program_id).details.config_class(),
                program_control_panel_dock=self._project_window.add_program_control_panel(program_id),
                parent=self,
                kwargs=kwargs,
            )
            self.addSubWindow(window)
            window.program.node_changed_signal.connect(
                lambda node_id, action: self._node_changed_handler(node_id, window.id, action)
            )
            window.program.send_message_signal.connect(self.program_send_message_signal.emit)
            window.program.update_control_panel_signal.connect(self._update_control_panel_handler)
            window.program.update_window_title_signal.connect(self._update_window_title_handler)
            window.show()
        except PluginNotFoundError:
            logger.error("Program `%s` is not registered", program_id)

    def update_program_event(self, program_id: str, apply_for_all: bool, key: str, data: dict[str, Any]):
        windows = self.subWindowList(QMdiArea.WindowOrder.ActivationHistoryOrder)
        i = 0
        for window in reversed(cast(list[_MdiProgramWindow], windows)):
            if window.program_id == program_id:
                window.program.action_event(key, data, i)
                i += 1
                if apply_for_all is False:
                    break
