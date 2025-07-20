"""
Rectangular 2D rectangle
By default, it's a square with a side length of 2 units.
"""

import numpy as np


def get_vertices(left: float = -1.0, right: float = 1.0, bottom: float = -1.0, top: float = 1.0) -> np.ndarray:
    vertices: list[float] = [
        left, bottom, 0.0,  # bottom left
        right, bottom, 0.0,  # bottom right
        right, top, 0.0,  # top right

        right, top, 0.0,  # top right
        left, top, 0.0,  # top left
        left, bottom, 0.0,  # bottom left
    ]
    return np.array(vertices, dtype=np.float32)


def get_texture_coords(u_min: float = 0.0, v_min: float = 0.0, u_max: float = 1.0, v_max: float = 1.0) -> np.ndarray:
    tex_coords: list[float] = [
        u_min, v_min,  # bottom left
        u_max, v_min,  # bottom right
        u_max, v_max,  # top right

        u_max, v_max,  # top right
        u_min, v_max,  # top left
        u_min, v_min,  # bottom left
    ]

    return np.array(tex_coords, dtype=np.float32)


def get_normals() -> np.ndarray:
    normals: list[float] = [
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,

        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
        0.0, 0.0, 1.0,
    ]
    return np.array(normals, dtype=np.float32)
