from math import cos, pi, sin

import numpy as np

min_stacks = 2
min_slices = 3


def get_vertices(stacks: int, slices: int) -> np.ndarray:
    radius: float = 1.0

    vertices: list[float] = []
    a = pi / stacks
    b = (pi * 2) / slices
    vertices.extend([0.0, radius, 0.0])
    for i in range(1, stacks):
        y = cos(a * i)
        for j in range(slices):
            x = sin(a * i) * cos(b * j)
            z = sin(a * i) * sin(b * j)
            vertices.extend([x * radius, y * radius, z * radius])
    vertices.extend([0.0, -radius, 0.0])
    return np.array(vertices, dtype=np.float32)


def get_faces(stacks: int, slices: int) -> np.ndarray:
    faces: list[int] = []
    # top cap
    for i in range(slices):
        faces.extend([0, ((i + 1) % slices) + 1, i + 1])

    # middle
    for stack in range(1, stacks - 1):
        for slice in range(slices):
            first = (stack - 1) * slices + 1 + slice
            second = first + slices
            next_slice = (slice + 1) % slices
            first_next = (stack - 1) * slices + 1 + next_slice
            second_next = first_next + slices

            faces.extend([first, first_next, second])
            faces.extend([first_next, second_next, second])

    # bottom cap
    last_vertex = (stacks - 1) * slices + 1
    for i in range(slices):
        faces.extend([last_vertex, last_vertex - slices + i, last_vertex - slices + ((i + 1) % slices)])
    return np.array(faces, dtype=np.int32)
