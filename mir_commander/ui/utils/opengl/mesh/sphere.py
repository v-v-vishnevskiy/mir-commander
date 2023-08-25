from math import cos, pi, sin

from mir_commander.ui.utils.opengl.mesh.base import MeshData


class Sphere(MeshData):
    min_rows = 6
    min_cols = 8

    def __init__(self, rows: int = 10, cols: int = 10):
        super().__init__()
        self._rows = self.min_rows
        self._cols = self.min_cols

        self.generate_mesh(rows, cols)

    def generate_mesh(self, rows: int, cols: int):
        self.vertices = []
        self._rows = max(self.min_rows, rows)
        self._cols = max(self.min_cols, cols)

        vertices = self._generate_vertices()
        faces = self._generate_faces()

        for i in faces:
            i *= 3
            self.vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])

    def _generate_vertices(self) -> list[float]:
        vertices = []
        a = pi / self._rows
        b = (pi * 2) / self._cols
        vertices.extend([0.0, 0.0, 1.0])
        for i in range(1, self._rows):
            z = cos(a * i)
            for j in range(self._cols):
                x = sin(a * i) * cos(b * j)
                y = sin(a * i) * sin(b * j)
                vertices.extend([x, y, z])
        vertices.extend([0.0, 0.0, -1.0])
        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []
        # the top
        prev_i = self._cols
        for i in range(1, self._cols + 1):
            faces.extend([0, prev_i, i])
            prev_i = i

        # the middle
        prev_row = 1
        for row in range(2, self._rows):
            prev_i = row * self._cols
            for i in range(prev_row * self._cols + 1, row * self._cols + 1):
                faces.extend([prev_i - self._cols, prev_i, i])
                faces.extend([i - self._cols, prev_i - self._cols, i])
                prev_i = i
            prev_row = row

        # the bottom
        num_vertices = (self._rows - 1) * self._cols + 2
        last_i = num_vertices - 1
        prev_i = last_i - 1
        for i in range(last_i - self._cols, last_i):
            faces.extend([i, prev_i, last_i])
            prev_i = i

        return faces
