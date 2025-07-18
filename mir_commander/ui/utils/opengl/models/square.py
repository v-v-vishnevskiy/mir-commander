import numpy as np


def get_vertices() -> np.ndarray:
    vertices: list[float] = [
        -1.0, -1.0, 0.0,
        1.0, -1.0, 0.0,
        1.0, 1.0, 0.0,

        1.0, 1.0, 0.0,
        -1.0, 1.0, 0.0,
        -1.0, -1.0, 0.0,
    ]
    return np.array(vertices, dtype=np.float32)


def get_texture_coords() -> np.ndarray:
    tex_coords: list[float] = [
        0.0, 0.0,
        1.0, 0.0,
        1.0, 1.0,

        1.0, 1.0,
        0.0, 1.0,
        0.0, 0.0,
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
