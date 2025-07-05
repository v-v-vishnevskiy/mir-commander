import numpy as np
from OpenGL.GL import (
    GL_FLOAT,
    GL_NORMAL_ARRAY,
    GL_TRIANGLES,
    GL_VERTEX_ARRAY,
    GLuint,
    glColor4f,
    glDisableClientState,
    glDrawArrays,
    glEnableClientState,
    glNormalPointer,
    glUseProgram,
    glVertexPointer,
)

from mir_commander.ui.utils.opengl.mesh import MeshData
from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.utils import Color4f

from ..default_shaders import PICKING_SHADER, SHADED
from ..enums import PaintMode

from .item import Item


class MeshItem(Item):
    default_shader: None | ShaderProgram = None
    _picking_shader: None | ShaderProgram = None

    def __init__(
        self,
        mesh_data: MeshData,
        smooth: bool = True,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
        shader: None | ShaderProgram = None,
    ):
        super().__init__()
        self._mesh_data = mesh_data
        self._smooth = smooth
        self._color = color

        if shader is None:
            if self.__class__.default_shader is None:
                self.__class__.default_shader = ShaderProgram(
                    VertexShader(SHADED["vertex"]), FragmentShader(SHADED["fragment"])
                )
            self._shader = self.__class__.default_shader
        else:
            self._shader = shader

        if self.__class__._picking_shader is None:
            self.__class__._picking_shader = ShaderProgram(
                VertexShader(PICKING_SHADER["vertex"]), FragmentShader(PICKING_SHADER["fragment"])
            )
        self._picking_shader = self.__class__._picking_shader

        self.set_smooth(smooth)

    @property
    def color(self) -> Color4f:
        return self._color

    def paint_self(self, mode: PaintMode):
        if not self.visible:
            return

        if mode == PaintMode.Picking:
            glUseProgram(self._picking_shader.program)
        else:
            glUseProgram(self.shader)

        glEnableClientState(GL_VERTEX_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, self._mesh_data.vertices)

        if mode == PaintMode.Picking:
            glColor4f(*self._picking_color)
        else:
            glColor4f(*self.color)

        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointer(GL_FLOAT, 0, self._normals)

        glDrawArrays(GL_TRIANGLES, 0, int(len(self._mesh_data.vertices) / 3))

        glDisableClientState(GL_NORMAL_ARRAY)
        glDisableClientState(GL_VERTEX_ARRAY)
        glUseProgram(0)

    @property
    def shader(self) -> GLuint:
        return self._shader.program

    @property
    def _normals(self) -> np.ndarray:
        if self._smooth:
            return self._mesh_data.vertex_normals
        else:
            return self._mesh_data.face_normals

    def set_color(self, color: Color4f):
        self._color = color

    def set_mesh_data(self, data: MeshData):
        self._mesh_data = data
        self.set_smooth(self._smooth)

    def set_smooth(self, smooth: bool):
        self._smooth = smooth
