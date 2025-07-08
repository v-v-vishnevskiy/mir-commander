from typing import Literal

import numpy as np
from pydantic import BaseModel, Field

class VolCube(BaseModel):
    """
    Class of 3D volume function represented as a cube of voxels.
    """
    data_type: Literal["volcube"] = "volcube"

    comment1: str = ""
    comment2: str = ""
    box_origin: list[float] = []
    steps_number: list[int] = []
    steps_size: list[list[float]] = []
    cube_data: np.ndarray = None
