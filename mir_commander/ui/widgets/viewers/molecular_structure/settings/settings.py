from typing import TYPE_CHECKING

from mir_commander.ui.utils.viewer.viewer_settings import ViewerSettings

from .coordinate_axes import CoordinateAxes
from .labels import Labels
from .volume_cube import VolumeCube

if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer


class Settings(ViewerSettings["MolecularStructureViewer"]):
    def __init__(self):
        super().__init__(apply_for_all_checkbox=True)

        self._coordinate_axes = CoordinateAxes(self)
        self._labels = Labels(self)
        self._volume_cube = VolumeCube(self)

        self.layout.addWidget(self._coordinate_axes)
        self.layout.addWidget(self._labels)
        self.layout.addWidget(self._volume_cube)
        self.layout.addStretch()

    def update_values(self, viewer: "MolecularStructureViewer"):
        self._coordinate_axes.update_values(viewer)
        self._labels.update_values(viewer)
        self._volume_cube.update_values(viewer)
