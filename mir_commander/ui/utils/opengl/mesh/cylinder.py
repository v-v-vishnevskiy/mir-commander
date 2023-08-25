from math import cos, pi, sin

from mir_commander.ui.utils.opengl.mesh.base import MeshData


class Cylinder(MeshData):
    min_cols = 8

    def __init__(self, cols: int = 10):
        super().__init__()
        self._cols = self.min_cols

        self.generate_mesh(cols)

    def generate_mesh(self, cols: int):
        self.vertices = []
        self._cols = max(self.min_cols, cols)

        vertices = self._generate_vertices()
        faces = self._generate_faces()

        for i in faces:
            i *= 3
            self.vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])

    def _generate_vertices(self) -> list[float]:
        vertices = []
        f = (pi * 2) / self._cols
        for z in [-0.5, 0.5]:
            for i in range(self._cols):
                x = cos(f * i)
                y = sin(f * i)
                vertices.extend([x, y, z])
        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []

        prev_i = self._cols - 1
        for i in range(self._cols):
            faces.extend([prev_i, i, i + self._cols])
            faces.extend([prev_i, i + self._cols, prev_i + self._cols])
            prev_i = i

        return faces
