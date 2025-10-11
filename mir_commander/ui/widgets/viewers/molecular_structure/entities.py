from dataclasses import dataclass

from mir_commander.ui.utils.opengl.utils import Color4f


@dataclass
class VolumeCubeIsosurface:
    id: int
    value: float
    factor: float
    color: Color4f
    visible: bool


@dataclass
class VolumeCubeIsosurfaceGroup:
    id: int
    isosurfaces: list[VolumeCubeIsosurface]
    visible: bool
