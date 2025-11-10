import numpy as np
from numpydantic import NDArray, Shape

from .base_data_structure import BaseDataStructure


class VolumeCube(BaseDataStructure):
    """
    Class of 3D volume function represented as a cube of voxels.
    """

    comment1: str = ""
    comment2: str = ""
    box_origin: list[float] = []
    steps_number: list[int] = []
    steps_size: list[list[float]] = []
    cube_data: NDArray[Shape["* x, * y, * z"], np.float64] = None  # noqa: F722
