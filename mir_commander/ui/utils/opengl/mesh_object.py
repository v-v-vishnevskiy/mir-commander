import numpy as np
from PySide6.QtCore import QCoreApplication

from mir_commander.ui.utils.opengl.mesh import MeshData
from mir_commander.ui.utils.opengl.vertex_array_object import VertexArrayObject


class MeshObject:
    __slots__ = ("vao", "mesh_data", "_smooth", "_id")

    def __init__(self, mesh_data: MeshData, smooth: bool = True):
        self._id = id(self)
        self.mesh_data = mesh_data
        self._smooth = smooth
        if QCoreApplication.instance().config.opengl.fallback_mode:
            self.vao = None
        else:
            self.vao = VertexArrayObject(mesh_data.vertices, self.normals)

    @property
    def id(self) -> int:
        return self._id

    @property
    def normals(self) -> np.ndarray:
        if self._smooth:
            return self.mesh_data.vertex_normals
        else:
            return self.mesh_data.face_normals
