import math
from typing import Literal

import numpy as np
from numpydantic import NDArray, Shape
from pydantic import BaseModel

from mir_commander.utils import consts


class VolumeCube(BaseModel):
    """
    Class of 3D volume function represented as a cube of voxels.
    """

    data_type: Literal["volume_cube"] = "volume_cube"

    comment1: str = ""
    comment2: str = ""
    box_origin: list[float] = []
    steps_number: list[int] = []
    steps_size: list[list[float]] = []
    cube_data: NDArray[Shape["* x, * y, * z"], np.float64] = None  # noqa: F722

    def find_points_xyz(self, value: float) -> tuple[list[float], list[float], list[float]]:
        """
        Find points in XYZ space (in Angstroms) with defined function value
        ToDo: use 3D interpolation of voxels (possibly in multi-threaded mode)
        """

        if self.cube_data is None:
            return [], [], []

        X = []
        Y = []
        Z = []
        for i in range(self.steps_number[0]):
            for j in range(self.steps_number[1]):
                for k in range(self.steps_number[2]):
                    if math.isclose(value, self.cube_data[i][j][k], rel_tol=1e-2):
                        x = (
                            self.steps_size[0][0] * i
                            + self.steps_size[0][1] * j
                            + self.steps_size[0][2] * k
                            + self.box_origin[0]
                        ) * consts.BOHR2ANGSTROM
                        y = (
                            self.steps_size[1][0] * i
                            + self.steps_size[1][1] * j
                            + self.steps_size[1][2] * k
                            + self.box_origin[1]
                        ) * consts.BOHR2ANGSTROM
                        z = (
                            self.steps_size[2][0] * i
                            + self.steps_size[2][1] * j
                            + self.steps_size[2][2] * k
                            + self.box_origin[2]
                        ) * consts.BOHR2ANGSTROM
                        X.append(x)
                        Y.append(y)
                        Z.append(z)

        return X, Y, Z
