import numpy as np
from numpydantic import NDArray, Shape

from mir_commander.plugin_system.project_node import ProjectNodeDataPlugin

from .utils import BaseProjectNode


class VolumeCubeData(ProjectNodeDataPlugin):
    """
    Class of 3D volume function represented as a cube of voxels.
    """

    comment1: str = ""
    comment2: str = ""
    box_origin: list[float] = []
    steps_number: list[int] = []
    steps_size: list[list[float]] = []
    cube_data: NDArray[Shape["* x, * y, * z"], np.float64] = None  # noqa: F722


class VolumeCubeNode(BaseProjectNode):
    def get_type(self) -> str:
        return "volume_cube"

    def get_name(self) -> str:
        return "Volume Cube"

    def get_icon_path(self) -> str:
        return ":/icons/project_nodes/volume_cube.png"

    def get_model_class(self) -> type[VolumeCubeData]:
        return VolumeCubeData

    def get_default_program_name(self) -> str:
        return "molecular_visualizer"

    def get_program_names(self) -> list[str]:
        return []
