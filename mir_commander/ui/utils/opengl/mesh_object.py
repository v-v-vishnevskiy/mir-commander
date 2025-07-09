import numpy as np
from PySide6.QtCore import QCoreApplication

from mir_commander.ui.utils.opengl.mesh import MeshData
from mir_commander.ui.utils.opengl.vertex_array_object import VertexArrayObject


class MeshObject:
    __slots__ = ("vao", "mesh_data", "_smooth")

    def __init__(self, mesh_data: MeshData, smooth: bool = True):
        self.mesh_data = mesh_data
        self._smooth = smooth
        if QCoreApplication.instance().config.opengl.fallback_mode:
            self.vao = None
        else:
            self.vao = VertexArrayObject(mesh_data.vertices, self.normals)

    @property
    def normals(self) -> np.ndarray:
        if self._smooth:
            return self.mesh_data.vertex_normals
        else:
            return self.mesh_data.face_normals

    def set_vertices(self, vertices: np.ndarray):
        self.mesh_data.set_vertices(vertices)
        if self.vao is not None:
            self.vao.update(self.mesh_data.vertices, self.normals)

    def set_smooth(self, smooth: bool):
        self._smooth = smooth
        if self.vao is not None:
            self.vao.update(self.mesh_data.vertices, self.normals)
