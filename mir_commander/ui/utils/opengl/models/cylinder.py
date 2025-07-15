from math import cos, pi, sin

import numpy as np

min_stacks = 1
min_slices = 3


def get_vertices(stacks: int, slices: int, radius: float = 1.0, length: float = 1.0, caps: bool = True) -> np.ndarray:
    vertices = []

    x_list = []
    y_list = []
    f = (pi * 2) / slices
    for i in range(slices):
        x_list.append(cos(f * i) * radius)
        y_list.append(sin(f * i) * radius)

    fraction = length / stacks
    start = 0.0
    z_list = [start]
    for _ in range(stacks):
        start += fraction
        z_list.append(start)

    if caps:
        vertices.extend([0.0, 0.0, z_list[0]])

    for z in z_list:
        for i in range(slices):
            vertices.extend([x_list[i], y_list[i], z])

    if caps:
        vertices.extend([0.0, 0.0, z_list[-1]])

    return np.array(vertices, dtype=np.float32)


def get_faces(stacks: int, slices: int, caps: bool = True) -> np.ndarray:
    faces = []

    # the top cap
    if caps:
        prev_i = slices
        for i in range(1, slices + 1):
            faces.extend([i, prev_i, 0])
            prev_i = i

    # the middle
    offset = 0
    if caps:
        offset = 1

    for stack in range(stacks):
        prev_i = slices - 1 + offset + (stack * slices)
        for i in range(slices):
            i += offset + (stack * slices)
            faces.extend([prev_i, i, i + slices])
            faces.extend([prev_i, i + slices, prev_i + slices])
            prev_i = i

    # the bottom cap
    if caps:
        num_vertices = (stacks + 1) * slices + 2
        last_i = num_vertices - 1
        prev_i = last_i - 1
        for i in range(last_i - slices, last_i):
            faces.extend([last_i, prev_i, i])
            prev_i = i

    return np.array(faces, dtype=np.int32)


def unwind_vertices(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    new_vertices = []
    for i in faces:
        i *= 3
        new_vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])
    return np.array(new_vertices, dtype=np.float32)
