from typing import TYPE_CHECKING

from mir_commander.api.program import ControlBlock
from mir_commander.api.program import ControlPanel as ControlPanelApi
from mir_commander.ui.sdk.widget import Label

from ..program import ControlComponent
from .control_elements.general import General

if TYPE_CHECKING:
    from .program import Program


class ControlPanel(ControlPanelApi):
    def __init__(self):
        super().__init__()

        self._blocks = [ControlBlock[ControlComponent](Label.tr("General"), General(self), True)]

    def allows_apply_for_all(self) -> bool:
        return True

    def get_blocks(self) -> list[ControlBlock]:
        return self._blocks

    def update_event(self, program: "Program"):
        for item in self._blocks:
            item.widget.update_values(program)

    def set_decimals(self, value: int):
        self.program_action_signal.emit("set_decimals", {"value": value})
