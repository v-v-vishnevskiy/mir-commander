from typing import TYPE_CHECKING

from mir_commander.api.program import ControlBlock
from mir_commander.api.program import ControlPanel as ControlPanelApi
from mir_commander.ui.sdk.widget import Label

from ..program import ControlComponent
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

        self._blocks = [
            ControlBlock[ControlComponent](Label.tr("View"), View(self), True),
            ControlBlock[ControlComponent](Label.tr("Atom labels"), AtomLabels(self), True),
            ControlBlock[ControlComponent](Label.tr("Cubes and surfaces"), VolumeCube(self), False),
            ControlBlock[ControlComponent](Label.tr("Image"), Image(self), False),
            ControlBlock[ControlComponent](Label.tr("Coordinate axes"), CoordinateAxes(self), False),
        ]

    def allows_apply_for_all(self) -> bool:
        return True

    def get_blocks(self) -> list[ControlBlock]:
        return self._blocks

    def update_event(self, program: "Program"):
        for item in self._blocks:
            item.widget.update_values(program)
