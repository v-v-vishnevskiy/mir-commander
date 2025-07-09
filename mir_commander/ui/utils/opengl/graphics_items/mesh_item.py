from OpenGL.GL import (
    GL_FLOAT,
    GL_NORMAL_ARRAY,
    GL_VERTEX_ARRAY,
    GL_TRIANGLES,
    glDrawArrays,
    glUseProgram,
    glUniformMatrix4fv,
    glBindVertexArray,
    glUniform4f,
    glLoadMatrixf,
    glEnableClientState,
    glNormalPointer,
    glVertexPointer,
    glColor4f,
    glDisableClientState,
)

from mir_commander.ui.utils.opengl.mesh_object import MeshObject
from mir_commander.ui.utils.opengl.shader import ShaderProgram
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
            self.paint_self = self.paint_self_fallback
        else:
            self.paint_self = self.paint_self_modern

    @property
    def color(self) -> Color4f:
        return self._color

    def paint_self_modern(self, mode: PaintMode, view_matrix: list[float], projection_matrix: list[float], shader: ShaderProgram):
        glUseProgram(shader.program)

        glUniform4f(shader.uniform_locations.color, *self.color)
        glUniformMatrix4fv(shader.uniform_locations.model_matrix, 1, False, self.get_transform.data())
        glUniformMatrix4fv(shader.uniform_locations.view_matrix, 1, False, view_matrix)
        glUniformMatrix4fv(shader.uniform_locations.projection_matrix, 1, False, projection_matrix)

        glBindVertexArray(self._vao.vao)

        glDrawArrays(GL_TRIANGLES, 0, self._vao.count)

        glBindVertexArray(0)

        glUseProgram(0)

    def paint_self_fallback(self, mode: PaintMode, view_matrix: list[float], projection_matrix: list[float], shader: ShaderProgram):
        glLoadMatrixf(self.get_transform.data())

        glUseProgram(shader.program)

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
        glUseProgram(0)

    def set_color(self, color: Color4f):
        self._color = color
