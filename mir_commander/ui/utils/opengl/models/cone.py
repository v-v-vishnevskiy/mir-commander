from math import cos, pi, sin

import numpy as np

min_stacks = 1
min_slices = 3


def get_vertices(stacks: int, slices: int, radius: float = 1.0, length: float = 1.0, cap: bool = True) -> np.ndarray:
    vertices = []

    x_list = []
    y_list = []
    f = (pi * 2) / slices
    for i in range(slices):
        x_list.append(cos(f * i))
        y_list.append(sin(f * i))

    fraction = length / stacks
    z_start = 0.0
    z_list = [z_start]
    for _ in range(stacks):
        z_start += fraction
        z_list.append(z_start)

    if cap:
        vertices.extend([0.0, 0.0, 0.0])

    for idx, z in enumerate(z_list):
        r = radius * (1.0 - z / length)
        for i in range(slices):
            vertices.extend([x_list[i] * r, y_list[i] * r, z])

    vertices.extend([0.0, 0.0, length])

    return np.array(vertices, dtype=np.float32)


def get_faces(stacks: int, slices: int, cap: bool = True) -> np.ndarray:
    faces = []

    # the base cap
    if cap:
        prev_i = slices
        for i in range(1, slices + 1):
            faces.extend([0, prev_i, i])
            prev_i = i

    # the middle (cone surface)
    offset = 0
    if cap:
        offset = 1

    for stack in range(stacks):
        prev_i = slices - 1 + offset + (stack * slices)
        for i in range(slices):
            i += offset + (stack * slices)
            faces.extend([prev_i, i, i + slices])
            faces.extend([prev_i, i + slices, prev_i + slices])
            prev_i = i

    # the tip (apex)
    num_vertices = (stacks + 1) * slices + 2 if cap else (stacks + 1) * slices + 1
    tip_i = num_vertices - 1
    prev_i = tip_i - 1
    for i in range(tip_i - slices, tip_i):
        faces.extend([tip_i, i, prev_i])
        prev_i = i

    return np.array(faces, dtype=np.int32)


def unwind_vertices(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    new_vertices = []
    for i in faces:
        i *= 3
        new_vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])
    return np.array(new_vertices, dtype=np.float32)
