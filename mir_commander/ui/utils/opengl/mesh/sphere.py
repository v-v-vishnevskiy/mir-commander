from math import cos, pi, sin

from .base import MeshData


class Sphere(MeshData):
    min_stacks = 2
    min_slices = 3
    min_radius = 0.001

    def __init__(self, stacks: int = 10, slices: int = 10, radius: float = 1.0):
        super().__init__()
        self.stacks = self.min_stacks
        self.slices = self.min_slices
        self.radius = self.min_radius

        self.generate_mesh(stacks, slices, radius)
        self._compute_vertex_normals()
        self._compute_face_normals()

    def generate_mesh(self, stacks: int, slices: int, radius: float = 1.0):
        self.stacks = max(self.min_stacks, stacks)
        self.slices = max(self.min_slices, slices)
        self.radius = max(self.min_radius, radius)

        vertices = self._generate_vertices()
        faces = self._generate_faces()

        new_vertices = []
        for i in range(0, len(faces), 3):
            for j in range(3):
                idx = faces[i + j]
                new_vertices.extend(vertices[idx*3:idx*3+3])
        self.set_vertices(new_vertices)

    def _generate_vertices(self) -> list[float]:
        vertices = []
        a = pi / self.stacks
        b = (pi * 2) / self.slices
        vertices.extend([0.0, 0.0, self.radius])
        for i in range(1, self.stacks):
            z = cos(a * i)
            for j in range(self.slices):
                x = sin(a * i) * cos(b * j)
                y = sin(a * i) * sin(b * j)
                vertices.extend([x * self.radius, y * self.radius, z * self.radius])
        vertices.extend([0.0, 0.0, -self.radius])
        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []
        # top cap
        for i in range(self.slices):
            faces.extend([0, i + 1, ((i + 1) % self.slices) + 1])

        # middle
        for stack in range(1, self.stacks - 1):
            for slice in range(self.slices):
                first = (stack - 1) * self.slices + 1 + slice
                second = first + self.slices
                next_slice = (slice + 1) % self.slices
                first_next = (stack - 1) * self.slices + 1 + next_slice
                second_next = first_next + self.slices

                faces.extend([first, second, first_next])
                faces.extend([first_next, second, second_next])

        # bottom cap
        last_vertex = (self.stacks - 1) * self.slices + 1
        for i in range(self.slices):
            faces.extend([
                last_vertex,
                last_vertex - self.slices + ((i + 1) % self.slices),
                last_vertex - self.slices + i
            ])
        return faces
