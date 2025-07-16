import logging
import numpy as np
import ctypes
from collections import defaultdict

from OpenGL.GL import (
    glUseProgram, 
    glUniformMatrix4fv, 
    glUniform4f, 
    glBindBuffer, 
    glBufferData, 
    glDrawArraysInstanced, 
    GL_ARRAY_BUFFER, 
    GL_TRIANGLES, 
    GL_STATIC_DRAW, 
    glGenBuffers, 
    glDrawArrays, 
    glEnableVertexAttribArray, 
    glVertexAttribPointer, 
    glVertexAttribDivisor, 
    GL_FLOAT, 
    glDeleteBuffers,
)

from mir_commander.ui.utils.opengl.shader import UniformLocations

from ..projection import ProjectionManager
from ..resource_manager import ResourceManager, SceneNode
from ..utils import Color4f

from .base import BaseRenderer

logger = logging.getLogger("OpenGL.ModernRenderer")


class ModernRenderer(BaseRenderer):
    def __init__(self, projection_manager: ProjectionManager, resource_manager: ResourceManager):
        super().__init__(projection_manager, resource_manager)
        self._transformation_buffers: dict[tuple[str, str, Color4f], tuple[int, int]] = {}

    def paint_opaque(self, nodes: list[SceneNode]):
        self._paint_normal(nodes)

    def paint_transparent(self, nodes: list[SceneNode]):
        self._paint_normal(nodes)

    def paint_picking(self, nodes: list[SceneNode]):
        shader = self._resource_manager.get_shader("picking")
        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)

        self._setup_uniforms(uniform_locations)

        nodes_by_vao: dict[str, list[SceneNode]] = defaultdict(list)
        for node in nodes:
            nodes_by_vao[node.vao].append(node)

        for vao, nodes in nodes_by_vao.items():
            vao = self._resource_manager.get_vertex_array_object(vao)
            vao.bind()
            for node in nodes:
                glUniform4f(uniform_locations.color, *node.picking_color)
                glUniformMatrix4fv(uniform_locations.model_matrix, 1, False, node.transform.data())
                glDrawArrays(GL_TRIANGLES, 0, vao.triangles_count)

    def _paint_normal(self, nodes: list[SceneNode]):
        nodes_by_shader = self._group_nodes(nodes)

        group_transform_dirty = self._resource_manager.current_scene.root_node.group_transform_dirty

        for shader_name, nodes_by_vao in nodes_by_shader.items():
            shader = self._resource_manager.get_shader(shader_name)
            glUseProgram(shader.program)
            uniform_locations = shader.uniform_locations
            self._setup_uniforms(uniform_locations)

            for vao_name, nodes_by_color in nodes_by_vao.items():
                vao = self._resource_manager.get_vertex_array_object(vao_name)
                vao.bind()

                for color, nodes in nodes_by_color.items():
                    buffer_key = (shader_name, vao_name, color)
                    buffer_id, nodes_count = self._get_transformation_buffer(buffer_key)
                    glBindBuffer(GL_ARRAY_BUFFER, buffer_id)

                    current_len_nodes = len(nodes)

                    if current_len_nodes != nodes_count or group_transform_dirty.get(buffer_key, False):
                        self._update_transformation_buffer(buffer_key, buffer_id, nodes)

                    self._setup_instanced_attributes()

                    glUniform4f(uniform_locations.color, *color)
                    glDrawArraysInstanced(GL_TRIANGLES, 0, vao.triangles_count, current_len_nodes)

    def _group_nodes(self, nodes: list[SceneNode]) -> dict[str, dict[str, dict[Color4f, list[SceneNode]]]]:
        """
        Returns a dictionary of nodes grouped by shader, vao, and color.
        """
        result = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for node in nodes:
            result[node.shader][node.vao][node.color].append(node)
        return result

    def _get_transformation_buffer(self, key: tuple[str, str, Color4f]) -> tuple[int, int]:
        if key not in self._transformation_buffers:
            buffer = glGenBuffers(1)
            self._transformation_buffers[key] = (buffer, 0)
        return self._transformation_buffers[key]

    def _update_transformation_buffer(self, key: tuple[str, str, Color4f], buffer: int, nodes: list[SceneNode]):
        transformation_data = []
        for node in nodes:
            transformation_data.extend(node.transform.data())
        transformation_array = np.array(transformation_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, transformation_array.nbytes, transformation_array, GL_STATIC_DRAW)
        self._transformation_buffers[key] = (buffer, len(nodes))

    def _setup_instanced_attributes(self):
        # Setup instanced attributes for transformation matrices
        # 4x4 matrix takes 4 attributes (location 2, 3, 4, 5)
        stride = 16 * 4  # 16 floats * 4 bytes per float
        for i in range(4):
            glEnableVertexAttribArray(2 + i)
            glVertexAttribPointer(2 + i, 4, GL_FLOAT, False, stride, ctypes.c_void_p(i * 4 * 4))
            glVertexAttribDivisor(2 + i, 1)  # Updated for each instance

    def _setup_uniforms(self, uniform_locations: UniformLocations):
        view_matrix = self._resource_manager.current_camera.matrix.data()
        scene_matrix = self._resource_manager.current_scene.transform.matrix.data()
        projection_matrix = self._projection_manager.active_projection.matrix.data()

        glUniformMatrix4fv(uniform_locations.view_matrix, 1, False, view_matrix)
        glUniformMatrix4fv(uniform_locations.scene_matrix, 1, False, scene_matrix)
        glUniformMatrix4fv(uniform_locations.projection_matrix, 1, False, projection_matrix)

    def __del__(self):
        for buffer, _ in self._transformation_buffers.values():
            glDeleteBuffers(1, [buffer])
