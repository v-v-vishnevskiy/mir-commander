from OpenGL.GL import glLoadMatrixf, glUseProgram

from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.shaders import fragment_fallback, vertex_fallback

from ..graphics_items.item import Item
from ..enums import PaintMode

from .base import BaseRenderer


class FallbackRenderer(BaseRenderer):
    def init_shaders(self):
        self._shaders["default"] = ShaderProgram(
            VertexShader(vertex_fallback.COMPUTE_POSITION), FragmentShader(fragment_fallback.BLINN_PHONG)
        )
        self._shaders["transparent"] = ShaderProgram(
            VertexShader(vertex_fallback.COMPUTE_POSITION), FragmentShader(fragment_fallback.FLAT_COLOR)
        )
        self._shaders["picking"] = ShaderProgram(
            VertexShader(vertex_fallback.COMPUTE_POSITION), FragmentShader(fragment_fallback.FLAT_COLOR)
        )

    def paint_opaque(self, items: list[Item], paint_mode: PaintMode):
        if paint_mode == PaintMode.Normal:
            shader = self._shaders["default"]
        else:
            shader = self._shaders["picking"]

        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        for item in items:
            glLoadMatrixf(item.get_transform.data())
            item.paint(paint_mode, uniform_locations)

    def paint_transparent(self, items: list[Item], paint_mode: PaintMode):
        if paint_mode == PaintMode.Normal:
            shader = self._shaders["transparent"]
        else:
            shader = self._shaders["picking"]

        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        for item in items:
            glLoadMatrixf(item.get_transform.data())
            item.paint(paint_mode, uniform_locations)
