import numpy as np
from PySide6.QtGui import QVector3D


class MeshData:
    __slots__ = ("vertices", "face_normals", "vertex_normals")

    def __init__(self):
        self.vertices: np.ndarray = np.array([], dtype=np.float32)
        self.face_normals: np.ndarray = np.array([], dtype=np.float32)
        self.vertex_normals: np.ndarray = np.array([], dtype=np.float32)

    def set_vertices(self, vertices: list[float]):
        self.vertices = np.array(vertices, dtype=np.float32)
        self._compute_vertex_normals()
        self._compute_face_normals()

    def _compute_vertex_normals(self):
        vertices = self.vertices

        normals = []
        for i in range(0, len(vertices), 3):
            norm = QVector3D(*vertices[i : i + 3])
            norm.normalize()
            normals.extend([norm.x(), norm.y(), norm.z()])
        self.vertex_normals = np.array(normals, dtype=np.float32)

    def _compute_face_normals(self):
        vertices = self.vertices

        normals = []
        for i in range(0, len(vertices), 9):
            norm = QVector3D().normal(
                QVector3D(*vertices[i : i + 3]),
                QVector3D(*vertices[i + 3 : i + 6]),
                QVector3D(*vertices[i + 6 : i + 9]),
            )
            norm = [norm.x(), norm.y(), norm.z()] * 3
            normals.extend(norm)
        self.face_normals = np.array(normals, dtype=np.float32)
