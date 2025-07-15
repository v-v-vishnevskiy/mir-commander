import logging
import numpy as np
import ctypes
from collections import defaultdict

from OpenGL.GL import glUseProgram, glUniformMatrix4fv, glBindVertexArray, glUniform4f, glBindBuffer, glBufferData, glDrawArraysInstanced, GL_ARRAY_BUFFER, GL_TRIANGLES, GL_STATIC_DRAW, glGenBuffers, glDrawArrays, glEnableVertexAttribArray, glVertexAttribPointer, glVertexAttribDivisor, GL_FLOAT, glDeleteBuffers

from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, UniformLocations, VertexShader
from mir_commander.ui.utils.opengl.shaders import fragment, vertex

from ..graphics_items.item import Item
from ..projection import ProjectionManager
from ..scene_graph import SceneGraph
from ..camera import Camera

from .base import BaseRenderer

logger = logging.getLogger("OpenGL.Renderer")


class ModernRenderer(BaseRenderer):
    def __init__(self, projection_manager: ProjectionManager, scene: SceneGraph, camera: Camera):
        super().__init__(projection_manager, scene, camera)
        self._transformation_buffers = {}

    def init_shaders(self):
        self._shaders["default"] = ShaderProgram(
            VertexShader(vertex.COMPUTE_POSITION_INSTANCED), FragmentShader(fragment.BLINN_PHONG)
        )
        self._shaders["transparent"] = ShaderProgram(
            VertexShader(vertex.COMPUTE_POSITION_INSTANCED), FragmentShader(fragment.FLAT_COLOR)
        )
        self._shaders["picking"] = ShaderProgram(
            VertexShader(vertex.COMPUTE_POSITION), FragmentShader(fragment.FLAT_COLOR)
        )

    def paint_opaque(self, items: list[Item]):
        shader = self._shaders["default"]

        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        self._setup_uniforms(uniform_locations)

        self._paint_normal(items, uniform_locations)

    def paint_transparent(self, items: list[Item]):
        shader = self._shaders["transparent"]

        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        self._setup_uniforms(uniform_locations)

        self._paint_normal(items, uniform_locations)

    def paint_picking(self, items: list[Item]):
        shader = self._shaders["picking"]
        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        self._setup_uniforms(uniform_locations)

        items_by_vao = defaultdict(list)
        for item in items:
            items_by_vao[item._vao.vao].append(item)

        for vao, items in items_by_vao.items():
            glBindVertexArray(vao)
            for item in items:
                glUniform4f(uniform_locations.color, *item.picking_color)
                glUniformMatrix4fv(uniform_locations.model_matrix, 1, False, item.get_transform.data())
                glDrawArrays(GL_TRIANGLES, 0, item._vao.count)

    def _paint_normal(self, items: list[Item], uniform_locations: UniformLocations):
        items_by_vao = defaultdict(list)
        set_transform_data = False
        for item in items:
            if item.transform_dirty:
                set_transform_data = True
                item.validate_transform()
            items_by_vao[(item._vao.vao, item.color)].append(item)

        for vao_color, vao_items in items_by_vao.items():
            vertex_count = int(len(vao_items[0]._mesh_data.vertices) / 3)

            vao, color = vao_color
            glBindVertexArray(vao)

            if vao_color not in self._transformation_buffers:
                buffer = glGenBuffers(1)
                self._transformation_buffers[vao_color] = (buffer, len(vao_items))
                set_transform_data = True

                glBindBuffer(GL_ARRAY_BUFFER, buffer)
            else:
                buffer, count = self._transformation_buffers[vao_color]
                glBindBuffer(GL_ARRAY_BUFFER, buffer)
                if count != len(vao_items):
                    self._transformation_buffers[vao_color] = (buffer, len(vao_items))
                    set_transform_data = True

            if set_transform_data:
                transformation_data = []
                for item in vao_items:
                    transformation_data.extend(item.get_transform.data())
                transformation_array = np.array(transformation_data, dtype=np.float32)
                glBufferData(GL_ARRAY_BUFFER, transformation_array.nbytes, transformation_array, GL_STATIC_DRAW)

            # Setup instanced attributes for transformation matrices
            # 4x4 matrix takes 4 attributes (location 2, 3, 4, 5)
            stride = 16 * 4  # 16 floats * 4 bytes per float
            for i in range(4):
                glEnableVertexAttribArray(2 + i)
                glVertexAttribPointer(2 + i, 4, GL_FLOAT, False, stride, ctypes.c_void_p(i * 4 * 4))
                glVertexAttribDivisor(2 + i, 1)  # Updated for each instance

            glUniform4f(uniform_locations.color, *color)
            glDrawArraysInstanced(GL_TRIANGLES, 0, vertex_count, len(vao_items))

    def _setup_uniforms(self, uniform_locations: UniformLocations):
        scene_matrix = self._scene.get_transform.data()
        view_matrix = self._camera.view_matrix.data()
        projection_matrix = self._projection_manager.active_projection.matrix.data()

        glUniformMatrix4fv(uniform_locations.scene_matrix, 1, False, scene_matrix)
        glUniformMatrix4fv(uniform_locations.view_matrix, 1, False, view_matrix)
        glUniformMatrix4fv(uniform_locations.projection_matrix, 1, False, projection_matrix)

    def __del__(self):
        for buffer, _ in self._transformation_buffers.values():
            glDeleteBuffers(1, [buffer])
