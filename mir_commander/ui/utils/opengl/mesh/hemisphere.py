from math import cos, pi, sin

from mir_commander.ui.utils.opengl.mesh.base import MeshData


class Hemisphere(MeshData):
    min_stacks = 1
    min_slices = 3
    min_radius = 0.001

    def __init__(self, stacks: int = 5, slices: int = 10, radius: float = 1.0):
        super().__init__()
        self.stacks = self.min_stacks
        self.slices = self.min_slices
        self.radius = self.min_radius

        self.generate_mesh(stacks, slices, radius)
        self.compute_vertex_normals()
        self.compute_face_normals()

    def generate_mesh(self, stacks: int, slices: int, radius: float = 1.0):
        self.stacks = max(self.min_stacks, stacks)
        self.slices = max(self.min_slices, slices)
        self.radius = max(self.min_radius, radius)

        vertices = self._generate_vertices()
        faces = self._generate_faces()

        new_vertices = []
        for i in faces:
            i *= 3
            new_vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])
        self.set_vertices(new_vertices)

    def _generate_vertices(self) -> list[float]:
        vertices = []
        a = (pi / 2) / self.stacks
        b = (pi * 2) / self.slices
        vertices.extend([0.0, 0.0, self.radius])
        for i in range(1, self.stacks + 1):
            z = cos(a * i)
            for j in range(self.slices):
                x = sin(a * i) * cos(b * j)
                y = sin(a * i) * sin(b * j)
                vertices.extend([x * self.radius, y * self.radius, z * self.radius])
        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []
        # the top
        prev_i = self.slices
        for i in range(1, self.slices + 1):
            faces.extend([0, prev_i, i])
            prev_i = i

        # the middle
        prev_stack = 1
        for stack in range(2, self.stacks + 1):
            prev_i = stack * self.slices
            for i in range(prev_stack * self.slices + 1, stack * self.slices + 1):
                faces.extend([prev_i - self.slices, prev_i, i])
                faces.extend([i - self.slices, prev_i - self.slices, i])
                prev_i = i
            prev_stack = stack

        return faces
