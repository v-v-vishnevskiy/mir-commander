from typing import TYPE_CHECKING

from mir_commander.api.program import ControlElement
from mir_commander.api.program import ControlPanel as ControlPanelApi
from mir_commander.ui.sdk.program_control_panel import ControlComponent
from mir_commander.ui.sdk.widget import Label

from .control_elements.atom_labels import AtomLabels
from .control_elements.coordinate_axes import CoordinateAxes
from .control_elements.image import Image
from .control_elements.view import View
from .control_elements.volume_cube import VolumeCube

if TYPE_CHECKING:
    from .program import Program


class ControlPanel(ControlPanelApi["Program"]):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self._control_elements = [
            ControlElement[ControlComponent](Label.tr("View"), View(self), True),
            ControlElement[ControlComponent](Label.tr("Atom labels"), AtomLabels(self), True),
            ControlElement[ControlComponent](Label.tr("Cubes and surfaces"), VolumeCube(self), False),
            ControlElement[ControlComponent](Label.tr("Image"), Image(self), False),
            ControlElement[ControlComponent](Label.tr("Coordinate axes"), CoordinateAxes(self), False),
        ]

    def allows_apply_for_all(self) -> bool:
        return True

    def get_control_elements(self) -> list[ControlElement]:
        return self._control_elements

    def update_event(self, program: "Program"):
        for control_element in self._control_elements:
            control_element.widget.update_values(program)
