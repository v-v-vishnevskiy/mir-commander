from typing import TYPE_CHECKING

from mir_commander.ui.utils.viewer.viewer_settings import ViewerSettings

from .coordinate_axes import CoordinateAxes
from .labels import Labels
from .rotation import Rotation
from .volume_cube import VolumeCube

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer


class Settings(ViewerSettings["MolecularStructureViewer"]):
    def __init__(self):
        super().__init__(apply_for_all_checkbox=True)

        self.coordinate_axes = CoordinateAxes(self)
        self.labels = Labels(self)
        self.volume_cube = VolumeCube(self)
        self.rotation = Rotation(self)

        self.layout.addWidget(self.rotation)
        self.layout.addWidget(self.coordinate_axes)
        self.layout.addWidget(self.labels)
        self.layout.addWidget(self.volume_cube)
        self.layout.addStretch()

    def update_values(self, viewer: "MolecularStructureViewer"):
        self.coordinate_axes.update_values(viewer)
        self.labels.update_values(viewer)
        self.volume_cube.update_values(viewer)
        self.rotation.update_values(viewer)
