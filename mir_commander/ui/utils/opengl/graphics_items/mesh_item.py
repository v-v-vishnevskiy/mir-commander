from typing import Union

from OpenGL.GL import (
    GL_FLOAT,
    GL_NORMAL_ARRAY,
    GL_TRIANGLES,
    GL_VERTEX_ARRAY,
    glColor4f,
    glDisableClientState,
    glDrawArrays,
    glEnableClientState,
    glNormalPointer,
    glVertexPointer,
)
from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.graphics_items.item import Item
from mir_commander.ui.utils.opengl.mesh import MeshData
from mir_commander.ui.utils.opengl.utils import Color4f


class MeshItem(Item):
    def __init__(
        self,
        mesh_data: MeshData,
        smooth: bool = False,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
        compute_normals: bool = True,
        parent: Union[None, "Item"] = None,
    ):
        super().__init__(parent)
        self._mesh_data = mesh_data
        self._smooth = smooth
        self._color = color
        self._normals: list[float] = []
        if compute_normals:
            self.compute_normals(smooth)

    def _compute_vertex_normals(self):
        self._normals.clear()
        vertices = self._mesh_data.vertices
        for i in range(0, len(vertices), 3):
            norm = QVector3D(*vertices[i : i + 3])
            norm.normalize()
            self._normals.extend([norm.x(), norm.y(), norm.z()])

    def _compute_face_normals(self):
        self._normals.clear()
        vertices = self._mesh_data.vertices
        for i in range(0, len(vertices), 9):
            norm = QVector3D().normal(
                QVector3D(*vertices[i : i + 3]),
                QVector3D(*vertices[i + 3 : i + 6]),
                QVector3D(*vertices[i + 6 : i + 9]),
            )
            norm = [norm.x(), norm.y(), norm.z()] * 3
            self._normals.extend(norm)

    def _paint_color(self):
        glColor4f(self._color)

    def _paint(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self._mesh_data.vertices)

        self._paint_color()

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, self._normals)

        glDrawArrays(GL_TRIANGLES, 0, int(len(self._mesh_data.vertices) / 3))

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    @property
    def normals(self) -> list[float]:
        return self._normals

    def set_mesh_data(self, data: MeshData):
        self._mesh_data = data

    def set_normals(self, normals: list[float]):
        self._normals = normals

    def compute_normals(self, smooth: bool = False):
        self._smooth = smooth
        if self._smooth:
            self._compute_vertex_normals()
        else:
            self._compute_face_normals()
