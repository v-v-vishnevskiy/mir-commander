from math import cos, pi, sin

from .base import MeshData


class Cylinder(MeshData):
    min_stacks = 1
    min_slices = 3
    min_radius = 0.001
    min_length = 0.001

    def __init__(self, stacks: int = 1, slices: int = 10, radius: float = 1.0, length: float = 1.0, caps: bool = True):
        super().__init__()
        self.stacks = self.min_stacks
        self.slices = self.min_slices
        self.radius = self.min_radius
        self.length = self.min_length
        self.caps = caps

        self.generate_mesh(stacks, slices, radius, length, caps)
        self._compute_vertex_normals()
        self._compute_face_normals()

    def generate_mesh(self, stacks: int, slices: int, radius: float = 1.0, length: float = 1.0, caps: bool = True):
        self.stacks = max(self.min_stacks, stacks)
        self.slices = max(self.min_slices, slices)
        self.radius = max(self.min_radius, radius)
        self.length = max(self.min_length, length)
        self.caps = caps

        vertices = self._generate_vertices()
        faces = self._generate_faces()

        new_vertices = []
        for i in faces:
            i *= 3
            new_vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])
        self.set_vertices(new_vertices)

    def _generate_vertices(self) -> list[float]:
        vertices = []

        x_list = []
        y_list = []
        f = (pi * 2) / self.slices
        for i in range(self.slices):
            x_list.append(cos(f * i) * self.radius)
            y_list.append(sin(f * i) * self.radius)

        fraction = self.length / self.stacks
        start = 0.0
        z_list = [start]
        for _ in range(self.stacks):
            start += fraction
            z_list.append(start)

        if self.caps:
            vertices.extend([0.0, 0.0, z_list[0]])

        for z in z_list:
            for i in range(self.slices):
                vertices.extend([x_list[i], y_list[i], z])

        if self.caps:
            vertices.extend([0.0, 0.0, z_list[-1]])

        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []

        # the top cap
        if self.caps:
            prev_i = self.slices
            for i in range(1, self.slices + 1):
                faces.extend([i, prev_i, 0])
                prev_i = i

        # the middle
        offset = 0
        if self.caps:
            offset = 1

        for stack in range(self.stacks):
            prev_i = self.slices - 1 + offset + (stack * self.slices)
            for i in range(self.slices):
                i += offset + (stack * self.slices)
                faces.extend([prev_i, i, i + self.slices])
                faces.extend([prev_i, i + self.slices, prev_i + self.slices])
                prev_i = i

        # the bottom cap
        if self.caps:
            num_vertices = (self.stacks + 1) * self.slices + 2
            last_i = num_vertices - 1
            prev_i = last_i - 1
            for i in range(last_i - self.slices, last_i):
                faces.extend([last_i, prev_i, i])
                prev_i = i

        return faces
