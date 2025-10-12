"""
3D cube model
By default, it's a cube with edge length of 2 units centered at origin.
"""

import numpy as np


def get_vertices(edge_length: float = 2.0) -> np.ndarray:
    """Generate cube vertices centered at origin."""
    half_edge = edge_length / 2.0

    vertices: list[float] = [
        # Front face
        -half_edge,
        -half_edge,
        half_edge,  # bottom left
        half_edge,
        -half_edge,
        half_edge,  # bottom right
        half_edge,
        half_edge,
        half_edge,  # top right
        -half_edge,
        half_edge,
        half_edge,  # top left
        # Back face
        -half_edge,
        -half_edge,
        -half_edge,  # bottom left
        half_edge,
        -half_edge,
        -half_edge,  # bottom right
        half_edge,
        half_edge,
        -half_edge,  # top right
        -half_edge,
        half_edge,
        -half_edge,  # top left
    ]

    return np.array(vertices, dtype=np.float32)


def get_faces() -> np.ndarray:
    """Generate cube face indices."""
    faces: list[int] = [
        # Front face
        0,
        1,
        2,
        0,
        2,
        3,
        # Back face
        4,
        6,
        5,
        4,
        7,
        6,
        # Left face
        4,
        0,
        3,
        4,
        3,
        7,
        # Right face
        1,
        5,
        6,
        1,
        6,
        2,
        # Top face
        3,
        2,
        6,
        3,
        6,
        7,
        # Bottom face
        4,
        5,
        1,
        4,
        1,
        0,
    ]

    return np.array(faces, dtype=np.int32)


def unwind_vertices(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """Convert indexed vertices to unwound vertex array."""
    new_vertices: list[float] = []
    for i in range(0, len(faces), 3):
        for j in range(3):
            idx = faces[i + j]
            new_vertices.extend(vertices[idx * 3 : idx * 3 + 3])
    return np.array(new_vertices, dtype=np.float32)


def get_normals() -> np.ndarray:
    """Generate cube face normals for unwound vertices."""
    normals: list[float] = []

    # Each face has 2 triangles (6 vertices), so we repeat each normal 6 times
    face_normals = [
        [0.0, 0.0, 1.0],  # Front face
        [0.0, 0.0, -1.0],  # Back face
        [-1.0, 0.0, 0.0],  # Left face
        [1.0, 0.0, 0.0],  # Right face
        [0.0, 1.0, 0.0],  # Top face
        [0.0, -1.0, 0.0],  # Bottom face
    ]

    for normal in face_normals:
        for _ in range(6):  # 6 vertices per face (2 triangles)
            normals.extend(normal)

    return np.array(normals, dtype=np.float32)
