import ctypes
import logging
from typing import Hashable

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_CULL_FACE,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FALSE,
    GL_FLOAT,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    GL_TRUE,
    glBindBuffer,
    glBlendFunc,
    glBufferData,
    glClear,
    glClearColor,
    glDeleteBuffers,
    glDepthMask,
    glDisable,
    glDrawArrays,
    glDrawArraysInstanced,
    glEnable,
    glEnableVertexAttribArray,
    glGenBuffers,
    glUniform4f,
    glUniformMatrix4fv,
    glUseProgram,
    glVertexAttribDivisor,
    glVertexAttribPointer,
    glViewport,
)
from PySide6.QtGui import QColor, QImage, QVector3D
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat

from .enums import PaintMode
from .projection import ProjectionManager
from .resource_manager import ResourceManager, UniformLocations
from .scene import BaseNode, RenderingContainer
from .utils import Color4f, crop_image_to_content

logger = logging.getLogger("OpenGL.Renderer")


class Renderer:
    def __init__(self, projection_manager: ProjectionManager, resource_manager: ResourceManager):
        self._projection_manager = projection_manager
        self._resource_manager = resource_manager
        self._bg_color = (0.0, 0.0, 0.0, 1.0)
        self._picking_image: None | QImage = None
        self._has_new_image = False
        self._transformation_buffers: dict[Hashable, tuple[int, int]] = {}

    def set_background_color(self, color: Color4f):
        self._bg_color = color

    def paint(self, paint_mode: PaintMode):
        normal_containers, text_rc, picking_rc = self._resource_manager.current_scene.containers

        glClearColor(*self._bg_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glDisable(GL_BLEND)

        if paint_mode == PaintMode.Picking:
            self._paint_picking(picking_rc)
        else:
            self._handle_text(text_rc)

            self._paint_normal(normal_containers["opaque"])

            if normal_containers["transparent"]:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glDepthMask(GL_FALSE)
                self._paint_normal(normal_containers["transparent"])
                glDepthMask(GL_TRUE)

            if normal_containers["char"]:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                self._paint_normal(normal_containers["char"])

            self._has_new_image = False

        self._resource_manager.current_scene.root_node.clear_dirty()

    def _handle_text(self, text_rc: RenderingContainer):
        for _, nodes in text_rc.batches:
            for node in nodes:
                node.update_char_translation(self._resource_manager.get_font_atlas(node.font_atlas_name))
        text_rc.clear()

    def _paint_picking(self, rc: RenderingContainer):
        prev_model_name = ""

        uniform_locations = self._setup_shader("", "picking")

        for group_id, nodes in rc.batches:
            _, _, model_name = group_id

            triangles_count = self._setup_vao(prev_model_name, model_name)
            prev_model_name = model_name

            # Draw nodes
            for node in nodes:
                glUniform4f(uniform_locations.color, *node.picking_color)
                glUniformMatrix4fv(uniform_locations.model_matrix, 1, False, node.transform.data())
                glDrawArrays(GL_TRIANGLES, 0, triangles_count)

    def _paint_normal(self, rc: RenderingContainer):
        prev_shader_name = ""
        prev_texture_name = ""
        prev_model_name = ""

        for group_id, nodes in rc.batches:
            shader_name, texture_name, model_name = group_id

            self._setup_shader(prev_shader_name, shader_name)
            prev_shader_name = shader_name

            prev_texture_name = self._setup_texture(prev_texture_name, texture_name)

            triangles_count = self._setup_vao(prev_model_name, model_name)
            prev_model_name = model_name

            self._setup_instanced_rendering(rc, group_id, nodes, texture_name != "")

            # OPTIMIZATION: Single draw call for all instances
            glDrawArraysInstanced(GL_TRIANGLES, 0, triangles_count, len(nodes))

    def _setup_shader(self, prev_shader_name: str, shader_name: str) -> UniformLocations:
        # OPTIMIZATION: Switch shader only when needed (expensive operation)
        shader = self._resource_manager.get_shader(shader_name)
        if shader_name != prev_shader_name:
            glUseProgram(shader.program)
            uniform_locations = shader.uniform_locations
            self._setup_uniforms(uniform_locations)
        return shader.uniform_locations

    def _setup_texture(self, prev_texture_name: str, texture_name: str):
        # OPTIMIZATION: Switch texture only when needed (expensive operation)
        if texture_name != "" and texture_name != prev_texture_name:
            texture = self._resource_manager.get_texture(texture_name)
            texture.bind()
            return texture_name
        # Unbind texture if needed
        elif texture_name == "" and prev_texture_name != "":
            texture = self._resource_manager.get_texture(prev_texture_name)
            texture.unbind()
            return texture_name
        return prev_texture_name

    def _setup_vao(self, prev_model_name: str, model_name: str) -> int:
        # OPTIMIZATION: Switch VAO only when needed (expensive operation)
        vao = self._resource_manager.get_vertex_array_object(model_name)
        if model_name != prev_model_name:
            vao.bind()
        return vao.triangles_count

    def _setup_instanced_rendering(self, rc: RenderingContainer, group_id: Hashable, nodes: list[BaseNode], has_texture: bool):
        # OPTIMIZATION: Use instanced rendering for multiple objects with same geometry
        (
            color_buffer_id,
            model_matrix_buffer_id,
            local_position_buffer_id,
            parent_local_position_buffer_id,
            parent_world_position_buffer_id,
            parent_parent_world_position_buffer_id,
        ) = self._get_transformation_buffer(group_id)

        # Update buffers if needed
        if rc._dirty.get(group_id, False):
            self._update_color_buffer(color_buffer_id, nodes)
            self._update_model_matrix_buffer(model_matrix_buffer_id, nodes)
            self._update_local_position_buffer(local_position_buffer_id, nodes)
            self._update_parent_local_position_buffer(parent_local_position_buffer_id, nodes)
            self._update_parent_world_position_buffer(parent_world_position_buffer_id, nodes)
            self._update_parent_parent_world_position_buffer(parent_parent_world_position_buffer_id, nodes)

        # Setup instanced attributes
        self._setup_color_attributes(color_buffer_id, 3 if has_texture else 2)
        self._setup_model_matrix_attributes(model_matrix_buffer_id, 4 if has_texture else 3)
        self._setup_position_attributes(local_position_buffer_id, 8 if has_texture else 7)
        self._setup_position_attributes(parent_local_position_buffer_id, 9 if has_texture else 8)
        self._setup_position_attributes(parent_world_position_buffer_id, 10 if has_texture else 9)
        self._setup_position_attributes(parent_parent_world_position_buffer_id, 11 if has_texture else 10)

    def _get_transformation_buffer(self, key: Hashable) -> tuple[int, int]:
        if key not in self._transformation_buffers:
            self._transformation_buffers[key] = (
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
            )
        return self._transformation_buffers[key]

    def _update_model_matrix_buffer(self, buffer_id: int, nodes: list[BaseNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        transformation_data = []
        for node in nodes:
            transformation_data.extend(node.transform.data())
        transformation_array = np.array(transformation_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, transformation_array.nbytes, transformation_array, GL_STATIC_DRAW)

    def _update_local_position_buffer(self, buffer_id: int, nodes: list[BaseNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data = []
        for node in nodes:
            data.extend(list(node._transform._translation.toTuple()))
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_color_buffer(self, buffer_id: int, nodes: list[BaseNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        color_data = []
        for node in nodes:
            color_data.extend(list(node.color))
        color_array = np.array(color_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, color_array.nbytes, color_array, GL_STATIC_DRAW)

    def _update_parent_local_position_buffer(self, buffer_id: int, nodes: list[BaseNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data = []
        for node in nodes:
            if node.parent is not None:
                data.extend(list(node.parent._transform._translation.toTuple()))
            else:
                data.extend([0.0, 0.0, 0.0])
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_parent_world_position_buffer(self, buffer_id: int, nodes: list[BaseNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data = []
        for node in nodes:
            if node.parent is not None:
                nd = node.parent.transform.data()
                center = QVector3D(nd[12], nd[13], nd[14])
                data.extend(list(center.toTuple()))
            else:
                data.extend([0.0, 0.0, 0.0])
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_parent_parent_world_position_buffer(self, buffer_id: int, nodes: list[BaseNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data = []
        for node in nodes:
            if node.parent is not None:
                if node.parent.parent is not None:
                    nd = node.parent.parent.transform.data()
                    center = QVector3D(nd[12], nd[13], nd[14])
                    data.extend(list(center.toTuple()))
                else:
                    nd = node.parent.transform.data()
                    center = QVector3D(nd[12], nd[13], nd[14])
                    data.extend(list(center.toTuple()))
            else:
                data.extend([0.0, 0.0, 0.0])
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _setup_model_matrix_attributes(self, buffer_id: int, index: int):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        # Setup instanced attributes for transformation matrices
        # 4x4 matrix takes 4 attributes (location 2, 3, 4, 5)
        stride = 16 * 4  # 16 floats * 4 bytes per float
        for i in range(4):
            glEnableVertexAttribArray(index + i)
            glVertexAttribPointer(index + i, 4, GL_FLOAT, False, stride, ctypes.c_void_p(i * 4 * 4))
            glVertexAttribDivisor(index + i, 1)  # Updated for each instance

    def _setup_position_attributes(self, buffer_id: int, index: int):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, 3, GL_FLOAT, False, 0, None)
        glVertexAttribDivisor(index, 1)

    def _setup_color_attributes(self, buffer_id: int, index: int):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, 4, GL_FLOAT, False, 0, None)
        glVertexAttribDivisor(index, 1)

    def _setup_uniforms(self, uniform_locations: UniformLocations):
        view_matrix = self._resource_manager.current_camera.matrix.data()
        scene_matrix = self._resource_manager.current_scene.transform.matrix.data()
        projection_matrix = self._projection_manager.active_projection.matrix.data()

        glUniformMatrix4fv(uniform_locations.view_matrix, 1, False, view_matrix)
        glUniformMatrix4fv(uniform_locations.scene_matrix, 1, False, scene_matrix)
        glUniformMatrix4fv(uniform_locations.projection_matrix, 1, False, projection_matrix)

    def _get_node_depth(self, node: BaseNode) -> float:
        point = QVector3D(0.0, 0.0, 0.0) * node.transform
        return self._resource_manager.current_camera.get_distance_to_point(point)

    def _sort_by_depth(self, nodes: list[BaseNode]) -> list[BaseNode]:
        return sorted(nodes, key=self._get_node_depth, reverse=True)

    def render_to_image(
        self, 
        width: int, 
        height: int, 
        transparent_bg: bool = False, 
        crop_to_content: bool = False,
        make_current_callback=None
    ) -> QImage:
        if make_current_callback:
            make_current_callback()

        fbo_format = QOpenGLFramebufferObjectFormat()
        fbo_format.setSamples(16)
        fbo_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        fbo = QOpenGLFramebufferObject(width, height, fbo_format)
        fbo.bind()

        bg_color_bak = self._bg_color

        if transparent_bg:
            self._bg_color = bg_color_bak[0], bg_color_bak[1], bg_color_bak[2], 0.0

        bg_color = QColor.fromRgbF(*self._bg_color)

        glViewport(0, 0, width, height)

        self.paint(PaintMode.Normal)

        self._bg_color = bg_color_bak

        fbo.release()

        image = fbo.toImage()

        if crop_to_content:
            image = crop_image_to_content(image, bg_color)

        return image

    def picking_image(self, width: int, height: int) -> QImage:
        if self._has_new_image:
            return self._picking_image

        fbo_format = QOpenGLFramebufferObjectFormat()
        fbo_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        fbo = QOpenGLFramebufferObject(width, height, fbo_format)
        fbo.bind()

        glViewport(0, 0, width, height)

        bg_color_bak = self._bg_color
        self._bg_color = (0.0, 0.0, 0.0, 1.0)

        self.paint(PaintMode.Picking)

        self._bg_color = bg_color_bak

        fbo.release()

        self._picking_image = fbo.toImage()
        self._has_new_image = True

        return self._picking_image

    def __del__(self):
        for buffers in self._transformation_buffers.values():
            glDeleteBuffers(1, list(buffers))
