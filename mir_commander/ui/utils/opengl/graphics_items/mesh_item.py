from OpenGL.GL import (
    GL_FLOAT,
    GL_NORMAL_ARRAY,
    GL_TRIANGLES,
    GL_VERTEX_ARRAY,
    glColor4f,
    glDisableClientState,
    glDrawArrays,
    glEnableClientState,
    glMultMatrixf,
    glNormalPointer,
    glPopMatrix,
    glPushMatrix,
    glUseProgram,
    glVertexPointer,
)
from PySide6.QtGui import QMatrix4x4

from mir_commander.ui.utils.opengl.default_shaders import SHADED
from mir_commander.ui.utils.opengl.graphics_items.item import Item
from mir_commander.ui.utils.opengl.mesh import MeshData
from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.utils import Color4f


class MeshItem(Item):
    default_shader: None | ShaderProgram = None

    def __init__(
        self,
        mesh_data: MeshData,
        smooth: bool = True,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
        shader: None | ShaderProgram = None,
    ):
        self.transform = QMatrix4x4()
        self._mesh_data = mesh_data
        self._smooth = smooth
        self._color = color
        self._normals: list[float] = []

        if shader is None:
            if self.__class__.default_shader is None:
                self.__class__.default_shader = ShaderProgram(
                    VertexShader(SHADED["vertex"]), FragmentShader(SHADED["fragment"])
                )
            self._shader = self.__class__.default_shader
        else:
            self._shader = shader

        self.set_smooth(smooth)

    @property
    def color(self) -> Color4f:
        return self._color

    def paint(self):
        glPushMatrix()
        glMultMatrixf(self.transform.data())

        glUseProgram(self._shader.program)
        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self._mesh_data.vertices)

        glColor4f(*self._color)

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, self._normals)

        glDrawArrays(GL_TRIANGLES, 0, int(len(self._mesh_data.vertices) / 3))

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glUseProgram(0)

        glPopMatrix()

    @property
    def normals(self) -> list[float]:
        return self._normals

    def set_color(self, color: Color4f):
        self._color = color

    def set_mesh_data(self, data: MeshData):
        self._mesh_data = data
        self.set_smooth(self._smooth)

    def set_normals(self, normals: list[float]):
        self._normals = normals

    def set_smooth(self, smooth: bool):
        self._smooth = smooth
        if self._smooth:
            self._normals = self._mesh_data.vertex_normals
        else:
            self._normals = self._mesh_data.face_normals
