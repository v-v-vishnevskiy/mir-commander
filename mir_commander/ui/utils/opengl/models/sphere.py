from math import cos, pi, sin

import numpy as np

min_stacks = 2
min_slices = 3


def get_vertices(stacks: int, slices: int, radius: float = 1.0) -> np.ndarray:
    vertices: list[float] = []
    a = pi / stacks
    b = (pi * 2) / slices
    vertices.extend([0.0, 0.0, radius])
    for i in range(1, stacks):
        z = cos(a * i)
        for j in range(slices):
            x = sin(a * i) * cos(b * j)
            y = sin(a * i) * sin(b * j)
            vertices.extend([x * radius, y * radius, z * radius])
    vertices.extend([0.0, 0.0, -radius])
    return np.array(vertices, dtype=np.float32)


def get_texture_coords(stacks: int, slices: int) -> np.ndarray:
    """Calculate texture coordinates for sphere using cylindrical projection.

    Args:
        stacks: Number of vertical stacks
        slices: Number of horizontal slices

    Returns:
        numpy array of texture coordinates (u, v) for each vertex
    """

    tex_coords: list[float] = []

    # Top pole - center of texture
    tex_coords.extend([0.5, 1.0])

    # Middle vertices
    for i in range(1, stacks):
        # v coordinate goes from 1.0 (top) to 0.0 (bottom)
        v = 1.0 - (i / (stacks - 1))
        for j in range(slices):
            # u coordinate goes from 0.0 to 1.0 around the sphere
            u = j / slices
            tex_coords.extend([u, v])

    # Bottom pole - center of texture
    tex_coords.extend([0.5, 0.0])

    return np.array(tex_coords, dtype=np.float32)


def get_faces(stacks: int, slices: int) -> np.ndarray:
    faces: list[int] = []
    # top cap
    for i in range(slices):
        faces.extend([0, i + 1, ((i + 1) % slices) + 1])

    # middle
    for stack in range(1, stacks - 1):
        for slice in range(slices):
            first = (stack - 1) * slices + 1 + slice
            second = first + slices
            next_slice = (slice + 1) % slices
            first_next = (stack - 1) * slices + 1 + next_slice
            second_next = first_next + slices

            faces.extend([first, second, first_next])
            faces.extend([first_next, second, second_next])

    # bottom cap
    last_vertex = (stacks - 1) * slices + 1
    for i in range(slices):
        faces.extend([
            last_vertex,
            last_vertex - slices + ((i + 1) % slices),
            last_vertex - slices + i
        ])
    return np.array(faces, dtype=np.int32)


def unwind_vertices(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    new_vertices = []
    for i in range(0, len(faces), 3):
        for j in range(3):
            idx = faces[i + j]
            new_vertices.extend(vertices[idx*3:idx*3+3])
    return np.array(new_vertices, dtype=np.float32)


def unwind_texture_coords(tex_coords: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """Unwind texture coordinates according to face indices.

    Args:
        tex_coords: Original texture coordinates array
        faces: Face indices array

    Returns:
        Unwound texture coordinates array
    """

    new_tex_coords = []
    for i in range(0, len(faces), 3):
        for j in range(3):
            idx = faces[i + j]
            new_tex_coords.extend(tex_coords[idx*2:idx*2+2])
    return np.array(new_tex_coords, dtype=np.float32)
