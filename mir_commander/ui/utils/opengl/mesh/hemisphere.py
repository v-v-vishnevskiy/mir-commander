from math import cos, pi, sin

from mir_commander.ui.utils.opengl.mesh.base import MeshData


class Hemisphere(MeshData):
    min_rows = 1
    min_cols = 3
    min_radius = 0.001

    def __init__(self, rows: int = 5, cols: int = 10, radius: float = 1.0):
        super().__init__()
        self.rows = self.min_rows
        self.cols = self.min_cols
        self.radius = self.min_radius

        self.generate_mesh(rows, cols, radius)
        self.compute_vertex_normals()
        self.compute_face_normals()

    def generate_mesh(self, rows: int, cols: int, radius: float = 1.0):
        self.rows = max(self.min_rows, rows)
        self.cols = max(self.min_cols, cols)
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
        a = (pi / 2) / self.rows
        b = (pi * 2) / self.cols
        vertices.extend([0.0, 0.0, self.radius])
        for i in range(1, self.rows + 1):
            z = cos(a * i)
            for j in range(self.cols):
                x = sin(a * i) * cos(b * j)
                y = sin(a * i) * sin(b * j)
                vertices.extend([x * self.radius, y * self.radius, z * self.radius])
        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []
        # the top
        prev_i = self.cols
        for i in range(1, self.cols + 1):
            faces.extend([0, prev_i, i])
            prev_i = i

        # the middle
        prev_row = 1
        for row in range(2, self.rows + 1):
            prev_i = row * self.cols
            for i in range(prev_row * self.cols + 1, row * self.cols + 1):
                faces.extend([prev_i - self.cols, prev_i, i])
                faces.extend([i - self.cols, prev_i - self.cols, i])
                prev_i = i
            prev_row = row

        return faces
