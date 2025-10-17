from typing import TYPE_CHECKING

from mir_commander.ui.utils.viewer.viewer_settings import ViewerSettings
from mir_commander.ui.utils.widget import Label

from .coordinate_axes import CoordinateAxes
from .image import Image
from .labels import Labels
from .view import View
from .volume_cube import VolumeCube

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer


class Settings(ViewerSettings["MolecularStructureViewer"]):
    def __init__(self):
        super().__init__(apply_for_all_checkbox=True)

        self.coordinate_axes = CoordinateAxes(self)
        self.labels = Labels(self)
        self.volume_cube = VolumeCube(self)
        self.view = View(self)
        self.image = Image(self)

        self.layout.add_widget(Label.tr("View"), self.view)
        self.layout.add_widget(Label.tr("Coordinate Axes"), self.coordinate_axes)
        self.layout.add_widget(Label.tr("Labels"), self.labels)
        self.layout.add_widget(Label.tr("Cubes and Surfaces"), self.volume_cube, False)
        self.layout.add_widget(Label.tr("Image"), self.image, False)
        self.layout.addStretch()

    def update_values(self, viewer: "MolecularStructureViewer"):
        self.coordinate_axes.update_values(viewer)
        self.labels.update_values(viewer)
        self.volume_cube.update_values(viewer)
        self.view.update_values(viewer)
        self.image.update_values(viewer)
