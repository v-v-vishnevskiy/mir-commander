from typing import TYPE_CHECKING

from mir_commander.ui.utils.program import ProgramControlPanel
from mir_commander.ui.utils.widget import Label

from .general import General

if TYPE_CHECKING:
    from ..program import CartesianEditor


class ControlPanel(ProgramControlPanel["CartesianEditor"]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **(kwargs | {"title": self.tr("Cartesian editor"), "apply_for_all_checkbox": True}))

        self.general = General(self)

        self.layout.add_widget(Label.tr("General"), self.general)
        self.layout.addStretch()

    def update_values(self, program: "CartesianEditor"):
        self.general.update_values(program)
