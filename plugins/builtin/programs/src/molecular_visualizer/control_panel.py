from typing import TYPE_CHECKING, Any, Iterable

from mir_commander.api.program import ControlBlock as ControlBlockApi
from mir_commander.api.program import ControlPanel as ControlPanelApi

from ..program import ControlBlock
from .control_elements.appearance import Appearance
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

        self._blocks = {
            "view": ControlBlockApi[ControlBlock](self.tr("View"), View(self), True),
            "atom_labels": ControlBlockApi[ControlBlock](self.tr("Atom labels"), AtomLabels(self), True),
            "cubes_and_surfaces": ControlBlockApi[ControlBlock](self.tr("Cubes and surfaces"), VolumeCube(self), False),
            "image": ControlBlockApi[ControlBlock](self.tr("Image"), Image(self), False),
            "coordinate_axes": ControlBlockApi[ControlBlock](self.tr("Coordinate axes"), CoordinateAxes(self), False),
            "appearance": ControlBlockApi[ControlBlock](self.tr("Appearance"), Appearance(self), False),
        }

    def allows_apply_for_all(self) -> bool:
        return True

    def get_blocks(self) -> Iterable[ControlBlockApi]:
        return self._blocks.values()

    def update_event(self, program: "Program", data: dict[Any, Any]):
        if "update_blocks" in data:
            for name in data["update_blocks"]:
                if name in self._blocks:
                    item = self._blocks[name]
                    item.widget.update_values(program)
        else:
            for item in self._blocks.values():
                item.widget.update_values(program)
