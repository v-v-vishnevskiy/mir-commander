from typing import TYPE_CHECKING

from mir_commander.ui.utils.program import ProgramControlPanel
from mir_commander.ui.utils.widget import Label

from .coordinate_axes import CoordinateAxes
from .image import Image
from .labels import Labels
from .view import View
from .volume_cube import VolumeCube

if TYPE_CHECKING:
    from ..program import MolecularVisualizer


class ControlPanel(ProgramControlPanel["MolecularVisualizer"]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **(kwargs | {"title": self.tr("Molecular visualizer"), "apply_for_all_checkbox": True}))

        self.coordinate_axes = CoordinateAxes(self)
        self.labels = Labels(self)
        self.volume_cube = VolumeCube(self)
        self.view = View(self)
        self.image = Image(self)

        self.layout.add_widget(Label.tr("View"), self.view)
        self.layout.add_widget(Label.tr("Coordinate axes"), self.coordinate_axes)
        self.layout.add_widget(Label.tr("Labels"), self.labels)
        self.layout.add_widget(Label.tr("Cubes and surfaces"), self.volume_cube, False)
        self.layout.add_widget(Label.tr("Image"), self.image, False)
        self.layout.addStretch()

    def update_values(self, program: "MolecularVisualizer"):
        self.coordinate_axes.update_values(program)
        self.labels.update_values(program)
        self.volume_cube.update_values(program)
        self.view.update_values(program)
        self.image.update_values(program)
