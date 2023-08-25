from math import cos, pi, sin

from mir_commander.ui.utils.opengl.mesh.base import MeshData


class Cylinder(MeshData):
    min_cols = 8
    min_radius = 0.001
    min_length = 0.001

    def __init__(self, cols: int = 10, radius: float = 1.0, length: float = 1.0):
        super().__init__()
        self._cols = self.min_cols
        self._radius = self.min_radius
        self._length = self.min_length

        self.generate_mesh(cols, radius, length)

    def generate_mesh(self, cols: int, radius: float = 1.0, length: float = 1.0):
        self.vertices = []
        self._cols = max(self.min_cols, cols)
        self._radius = max(self.min_radius, radius)
        self._length = max(self.min_length, length)

        vertices = self._generate_vertices()
        faces = self._generate_faces()

        for i in faces:
            i *= 3
            self.vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])

    def _generate_vertices(self) -> list[float]:
        vertices = []
        f = (pi * 2) / self._cols
        for z in [-0.5 * self._length, 0.5 * self._length]:
            for i in range(self._cols):
                x = cos(f * i)
                y = sin(f * i)
                vertices.extend([x * self._radius, y * self._radius, z])
        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []

        prev_i = self._cols - 1
        for i in range(self._cols):
            faces.extend([prev_i, i, i + self._cols])
            faces.extend([prev_i, i + self._cols, prev_i + self._cols])
            prev_i = i

        return faces
