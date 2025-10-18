from dataclasses import dataclass

from mir_commander.ui.utils.opengl.utils import Color4f


@dataclass
class VolumeCubeIsosurface:
    id: int
    inverted: bool
    color: Color4f
    visible: bool


@dataclass
class VolumeCubeIsosurfaceGroup:
    id: int
    value: float
    isosurfaces: list[VolumeCubeIsosurface]
    visible: bool
