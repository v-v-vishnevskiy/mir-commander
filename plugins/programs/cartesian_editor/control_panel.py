from typing import TYPE_CHECKING

from mir_commander.api.program import ControlElement
from mir_commander.api.program import ControlPanel as ControlPanelApi
from mir_commander.ui.sdk.widget import Label

from ..program import ControlComponent
from .control_elements.general import General

if TYPE_CHECKING:
    from .program import Program


class ControlPanel(ControlPanelApi):
    def __init__(self):
        super().__init__()

        self._control_elements = [ControlElement[ControlComponent](Label.tr("General"), General(self), True)]

    def allows_apply_for_all(self) -> bool:
        return True

    def get_control_elements(self) -> list[ControlElement]:
        return self._control_elements

    def update_event(self, program: "Program"):
        for control_element in self._control_elements:
            control_element.widget.update_values(program)

    def set_decimals(self, value: int):
        self.update_program_signal.emit("general.set_decimals", {"value": value})
