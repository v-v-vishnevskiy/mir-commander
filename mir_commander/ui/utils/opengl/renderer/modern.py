import logging
from collections import defaultdict

from OpenGL.GL import glUseProgram, glUniformMatrix4fv, glBindVertexArray, GLuint, glUniform4f

from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, UniformLocations, VertexShader
from mir_commander.ui.utils.opengl.shaders import fragment, vertex

from ..graphics_items.item import Item
from ..enums import PaintMode

from .base import BaseRenderer

logger = logging.getLogger("OpenGL.Renderer")


class ModernRenderer(BaseRenderer):
    def init_shaders(self):
        self._shaders["default"] = ShaderProgram(
            VertexShader(vertex.COMPUTE_POSITION), FragmentShader(fragment.BLINN_PHONG)
        )
        self._shaders["transparent"] = ShaderProgram(
            VertexShader(vertex.COMPUTE_POSITION), FragmentShader(fragment.FLAT_COLOR)
        )
        self._shaders["picking"] = ShaderProgram(
            VertexShader(vertex.COMPUTE_POSITION), FragmentShader(fragment.FLAT_COLOR)
        )

    def paint_opaque(self, items: list[Item], paint_mode: PaintMode):
        if paint_mode == PaintMode.Normal:
            shader = self._shaders["default"]
        else:
            shader = self._shaders["picking"]

        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        self._setup_uniforms(uniform_locations)

        items_by_vao = defaultdict(list)
        for item in items:
            items_by_vao[(item._vao.vao, item.color)].append(item)

        for vao_color, items in items_by_vao.items():
            vao, color = vao_color
            glBindVertexArray(vao)
            glUniform4f(uniform_locations.color, *color)
            for item in items:
                if paint_mode == PaintMode.Picking:
                    glUniform4f(uniform_locations.color, *item._picking_color)
                glUniformMatrix4fv(uniform_locations.model_matrix, 1, False, item.get_transform.data())
                item.paint(paint_mode)

    def paint_transparent(self, items: list[Item], paint_mode: PaintMode):
        if paint_mode == PaintMode.Normal:
            shader = self._shaders["transparent"]
        else:
            shader = self._shaders["picking"]

        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        self._setup_uniforms(uniform_locations)

        items_by_vao: list[dict[GLuint, list[Item]]] = []
        last_vao_color = None
        for item in items:
            vao_color = (item._vao.vao, item.color)
            if last_vao_color != vao_color:
                items_by_vao.append({vao_color: [item]})
                last_vao_color = vao_color
            else:
                items_by_vao[-1][vao_color].append(item)

        for vao_items in items_by_vao:
            for vao_color, items in vao_items.items():
                vao, color = vao_color
                glBindVertexArray(vao)
                glUniform4f(uniform_locations.color, *color)
                for item in items:
                    if paint_mode == PaintMode.Picking:
                        glUniform4f(uniform_locations.color, *item._picking_color)
                    glUniformMatrix4fv(uniform_locations.model_matrix, 1, False, item.get_transform.data())
                    item.paint(paint_mode)

    def _setup_uniforms(self, uniform_locations: UniformLocations):
        view_matrix = self._camera.view_matrix.data()
        projection_matrix = self._projection_manager.active_projection.matrix.data()

        glUniformMatrix4fv(uniform_locations.view_matrix, 1, False, view_matrix)
        glUniformMatrix4fv(uniform_locations.projection_matrix, 1, False, projection_matrix)
