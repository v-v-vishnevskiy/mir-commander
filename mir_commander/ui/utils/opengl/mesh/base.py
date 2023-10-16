from PySide6.QtGui import QVector3D


class MeshData:
    def __init__(self, vertices: None | list[float] = None):
        self.vertices: list[float] = vertices or []
        self.face_normals: list[float] = []
        self.vertex_normals: list[float] = []

    def compute_vertex_normals(self):
        self.vertex_normals.clear()
        vertices = self.vertices

        for i in range(0, len(vertices), 3):
            norm = QVector3D(*vertices[i : i + 3])
            norm.normalize()
            self.vertex_normals.extend([norm.x(), norm.y(), norm.z()])

    def compute_face_normals(self):
        self.face_normals.clear()
        vertices = self.vertices

        for i in range(0, len(vertices), 9):
            norm = QVector3D().normal(
                QVector3D(*vertices[i : i + 3]),
                QVector3D(*vertices[i + 3 : i + 6]),
                QVector3D(*vertices[i + 6 : i + 9]),
            )
            norm = [norm.x(), norm.y(), norm.z()] * 3
            self.face_normals.extend(norm)
