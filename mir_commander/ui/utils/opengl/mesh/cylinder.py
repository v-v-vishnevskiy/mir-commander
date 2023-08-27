from math import cos, pi, sin

from mir_commander.ui.utils.opengl.mesh.base import MeshData


class Cylinder(MeshData):
    min_rows = 1
    min_cols = 3
    min_radius = 0.001
    min_length = 0.001

    def __init__(self, rows: int = 1, cols: int = 10, radius: float = 1.0, length: float = 1.0, caps: bool = True):
        super().__init__()
        self._rows = self.min_rows
        self._cols = self.min_cols
        self._radius = self.min_radius
        self._length = self.min_length
        self._caps = caps

        self.generate_mesh(rows, cols, radius, length, caps)

    def generate_mesh(self, rows: int, cols: int, radius: float = 1.0, length: float = 1.0, caps: bool = True):
        self.vertices = []
        self._rows = max(self.min_rows, rows)
        self._cols = max(self.min_cols, cols)
        self._radius = max(self.min_radius, radius)
        self._length = max(self.min_length, length)
        self._caps = caps

        vertices = self._generate_vertices()
        faces = self._generate_faces()

        for i in faces:
            i *= 3
            self.vertices.extend([vertices[i], vertices[i + 1], vertices[i + 2]])

    def _generate_vertices(self) -> list[float]:
        vertices = []

        x_list = []
        y_list = []
        f = (pi * 2) / self._cols
        for i in range(self._cols):
            x_list.append(cos(f * i) * self._radius)
            y_list.append(sin(f * i) * self._radius)

        fraction = self._length / self._rows
        start = -(self._length / 2.0)
        z_list = [start]
        for _ in range(self._rows):
            start += fraction
            z_list.append(start)

        if self._caps:
            vertices.extend([0.0, 0.0, z_list[0]])

        for z in z_list:
            for i in range(self._cols):
                vertices.extend([x_list[i], y_list[i], z])

        if self._caps:
            vertices.extend([0.0, 0.0, z_list[-1]])

        return vertices

    def _generate_faces(self) -> list[int]:
        faces = []

        # the top cap
        if self._caps:
            prev_i = self._cols
            for i in range(1, self._cols + 1):
                faces.extend([i, prev_i, 0])
                prev_i = i

        # the middle
        offset = 0
        if self._caps:
            offset = 1

        for row in range(self._rows):
            prev_i = self._cols - 1 + offset + (row * self._cols)
            for i in range(self._cols):
                i += offset + (row * self._cols)
                faces.extend([prev_i, i, i + self._cols])
                faces.extend([prev_i, i + self._cols, prev_i + self._cols])
                prev_i = i

        # the bottom cap
        if self._caps:
            num_vertices = (self._rows + 1) * self._cols + 2
            last_i = num_vertices - 1
            prev_i = last_i - 1
            for i in range(last_i - self._cols, last_i):
                faces.extend([last_i, prev_i, i])
                prev_i = i

        return faces
