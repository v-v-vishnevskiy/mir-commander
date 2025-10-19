from typing import TYPE_CHECKING, Any, cast

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QMdiArea

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.program import ProgramControlPanel, ProgramWindow
from mir_commander.ui.widgets.docks.project_dock.items import TreeItem

if TYPE_CHECKING:
    from .project_window import ProjectWindow


class MdiArea(QMdiArea):
    opened_program_signal = Signal(ProgramWindow)

    def __init__(self, project_window: "ProjectWindow", app_config: AppConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._project_window = project_window
        self._app_config = app_config

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.subWindowActivated.connect(self._sub_window_activated_handler)

    def open_program(self, item: TreeItem, program_cls: type[ProgramWindow], kwargs: dict[str, Any]):
        for program in self.subWindowList():
            # checking if program for this item already opened
            if isinstance(program, program_cls) and program.item == item:
                self.setActiveSubWindow(program)
                break
        else:
            program = program_cls(
                parent=self,
                app_config=self._app_config,
                item=item,
                control_panel=self._add_program_control_panel(program_cls),
                **kwargs,
            )
            self.opened_program_signal.emit(program)
            self.addSubWindow(program)
        program.show()

    def _add_program_control_panel(self, program_cls: type[ProgramWindow]) -> ProgramControlPanel | None:
        if program_cls.control_panel_cls is None:
            return None
        return self._project_window.add_program_control_panel(program_cls.control_panel_cls)

    def _sub_window_activated_handler(self, window: None | ProgramWindow):
        programs_control_panels = self._project_window.programs_control_panels
        grouped_programs: dict[type[ProgramControlPanel], list[ProgramWindow]] = {
            k: [] for k in programs_control_panels.keys()
        }
        for w in self.subWindowList():
            program = cast(ProgramWindow, w)
            control_panel_cls = program.control_panel_cls
            if control_panel_cls is None:
                continue
            grouped_programs[control_panel_cls].append(program)

        for control_panel_cls, programs in grouped_programs.items():
            if control_panel := programs_control_panels.get(control_panel_cls):
                control_panel.set_opened_programs(programs)

        if window is not None and window.control_panel_cls is not None:
            if control_panel := programs_control_panels.get(window.control_panel_cls):
                control_panel.set_active_program(window)
