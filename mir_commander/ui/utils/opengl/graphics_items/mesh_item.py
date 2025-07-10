from OpenGL.GL import (
    GL_FLOAT,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
    GL_TRIANGLES,
    glDrawArrays,
    glEnableClientState,
    glNormalPointer,
    glVertexPointer,
    glColor4f,
    glDisableClientState,
)

from mir_commander.ui.utils.opengl.mesh_object import MeshObject
from mir_commander.ui.utils.opengl.utils import Color4f

from ..enums import PaintMode

from .item import Item


class MeshItem(Item):
    def __init__(
        self,
        mesh_object: MeshObject,
        smooth: bool = True,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
    ):
        super().__init__()
        self._mesh_object = mesh_object
        self._mesh_data = mesh_object.mesh_data
        self._vao = mesh_object.vao
        self._smooth = smooth
        self._color = color
        self._count = int(len(self._mesh_data.vertices) / 3)

        if self._vao is None:
            self.paint = self.paint_fallback
        else:
            self.paint = self.paint_modern

    @property
    def color(self) -> Color4f:
        return self._color

    def paint_modern(self, mode: PaintMode):
        glDrawArrays(GL_TRIANGLES, 0, self._vao.count)

    def paint_fallback(self, mode: PaintMode):
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self._mesh_data.vertices)

        if mode == PaintMode.Picking:
            glColor4f(*self._picking_color)
        else:
            glColor4f(*self.color)

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, self._mesh_object.normals)

        glDrawArrays(GL_TRIANGLES, 0, int(len(self._mesh_data.vertices) / 3))

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)

    def set_color(self, color: Color4f):
        self._color = color
