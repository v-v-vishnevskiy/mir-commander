import ctypes
import logging
import numpy as np
from typing import Hashable

from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_CULL_FACE,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_FLOAT,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    GL_STATIC_DRAW,
    GL_TRIANGLES,
    glBindBuffer,
    glBlendFunc,
    glBufferData,
    glClear,
    glClearColor,
    glDeleteBuffers,
    glDisable,
    glDrawArrays,
    glDrawArraysInstanced,
    glEnable,
    glEnableVertexAttribArray,
    glGenBuffers,
    glUniform4f,
    glUniformMatrix4fv,
    glUseProgram,
    glVertexAttribPointer,
    glVertexAttribDivisor,
    glViewport,
)
from PySide6.QtGui import QColor, QImage, QVector3D
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat

from .enums import PaintMode
from .projection import ProjectionManager
from .resource_manager import RenderingContainer, ResourceManager, SceneNode, SceneTextNode, UniformLocations
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
        opaque_rc, transparent_rc, text_rc, picking_rc = self._resource_manager.current_scene.containers()

        self._handle_text(text_rc)

        glClearColor(*self._bg_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glDisable(GL_BLEND)

        if paint_mode == PaintMode.Picking:
            self._paint_picking(picking_rc)
        else:
            self._paint_normal(opaque_rc)

            if transparent_rc:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glDisable(GL_DEPTH_TEST)
                self._paint_normal(transparent_rc)

            self._has_new_image = False

        self._resource_manager.current_scene.root_node.clear_transform_dirty()

    def _handle_text(self, text_rc: RenderingContainer):
        for group_id, nodes in text_rc.batches:
            for node in nodes:
                if node.has_new_text:
                    self._update_char_translation(node)
                    node._has_new_text = False

    def _update_char_translation(self, node: SceneTextNode):
        x_offset = 0.0
        children = node.nodes

        font_atlas_name = node.font_atlas_name
        font_atlas = self._resource_manager.get_font_atlas(font_atlas_name)

        x_offset = 0.0
        for i, char in enumerate(node.text):
            info = font_atlas.info[char]
            half_width = info["width"] / info["height"]
            x = half_width + x_offset
            children[i].translate(QVector3D(x, 0.0, 0.0))
            x_offset += half_width * 2

        if node.align == "center":
            vector = QVector3D(-x_offset / 2, 0.0, 0.0)
        elif node.align == "right":
            vector = QVector3D(-x_offset, 0.0, 0.0)
        else:
            vector = QVector3D(0.0, 0.0, 0.0)

        nd = node.transform.data()
        center = QVector3D(nd[12], nd[13], nd[14])

        for n in node.nodes:
            n.translate(vector)
            n.center = center

    def _paint_picking(self, rc: RenderingContainer):
        shader = self._resource_manager.get_shader("picking")
        uniform_locations = shader.uniform_locations
        glUseProgram(shader.program)
        self._setup_uniforms(uniform_locations)

        last_model_name = None

        for group_id, nodes in rc.batches:
            _, _, model_name = group_id

            # Switch VAO if needed
            if model_name != last_model_name:
                vao = self._resource_manager.get_vertex_array_object(model_name)
                vao.bind()
                last_model_name = model_name

            # Draw nodes
            for node in nodes:
                glUniform4f(uniform_locations.color, *node.picking_color)
                glUniformMatrix4fv(uniform_locations.model_matrix, 1, False, node.transform.data())
                glDrawArrays(GL_TRIANGLES, 0, vao.triangles_count)

    def _paint_normal(self, rc: RenderingContainer):
        last_shader_name = None
        last_model_name = None
        last_texture_name = None

        for group_id, nodes in rc.batches:
            shader_name, texture_name, model_name = group_id

            # OPTIMIZATION: Switch shader only when needed (expensive operation)
            if shader_name != last_shader_name:
                try:
                    shader = self._resource_manager.get_shader(shader_name)
                except ValueError:
                    logger.warning(f"Shader `{shader_name}` not found, skipping group")
                    continue

                glUseProgram(shader.program)
                uniform_locations = shader.uniform_locations
                self._setup_uniforms(uniform_locations)
                last_shader_name = shader_name

            # OPTIMIZATION: Switch texture only when needed (expensive operation)
            if texture_name is not None and texture_name != last_texture_name:
                texture = self._resource_manager.get_texture(texture_name)
                texture.bind()
                last_texture_name = texture_name
            # Unbind texture if needed
            elif texture_name is None and last_texture_name is not None:
                texture = self._resource_manager.get_texture(last_texture_name)
                texture.unbind()
                last_texture_name = texture_name

            # OPTIMIZATION: Switch VAO only when needed (expensive operation)
            if model_name != last_model_name:
                vao = self._resource_manager.get_vertex_array_object(model_name)
                vao.bind()
                last_model_name = model_name

            # OPTIMIZATION: Use instanced rendering for multiple objects with same geometry
            color_buffer_id, local_pos_buffer_id, center_buffer_id, model_matrix_buffer_id, nodes_count = self._get_transformation_buffer(group_id)

            # Update transformation buffer if needed
            current_len_nodes = len(nodes)
            if current_len_nodes != nodes_count or rc.transform_dirty.get(group_id, False):
                self._update_model_matrix_buffer(model_matrix_buffer_id, nodes)
                self._update_color_buffer(color_buffer_id, nodes)
                self._update_center_buffer(center_buffer_id, nodes)
                self._update_local_pos_buffer(local_pos_buffer_id, nodes)
                self._transformation_buffers[group_id] = (color_buffer_id, local_pos_buffer_id, center_buffer_id, model_matrix_buffer_id, len(nodes))

            # Setup instanced attributes
            self._setup_local_pos_attributes(local_pos_buffer_id, 2 if texture_name is None else 3)
            self._setup_center_attributes(center_buffer_id, 3 if texture_name is None else 4)
            self._setup_color_attributes(color_buffer_id, 4 if texture_name is None else 5)
            self._setup_model_matrix_attributes(model_matrix_buffer_id, 5 if texture_name is None else 6)

            # OPTIMIZATION: Single draw call for all instances
            glDrawArraysInstanced(GL_TRIANGLES, 0, vao.triangles_count, current_len_nodes)

    def _get_transformation_buffer(self, key: Hashable) -> tuple[int, int]:
        if key not in self._transformation_buffers:
            color_buffer_id = glGenBuffers(1)
            local_pos_buffer_id = glGenBuffers(1)
            center_buffer_id = glGenBuffers(1)
            model_matrix_buffer_id = glGenBuffers(1)
            self._transformation_buffers[key] = (color_buffer_id, local_pos_buffer_id, center_buffer_id, model_matrix_buffer_id, 0)
        return self._transformation_buffers[key]

    def _update_model_matrix_buffer(self, buffer_id: int, nodes: list[SceneNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        transformation_data = []
        for node in nodes:
            transformation_data.extend(node.transform.data())
        transformation_array = np.array(transformation_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, transformation_array.nbytes, transformation_array, GL_STATIC_DRAW)

    def _update_center_buffer(self, buffer_id: int, nodes: list[SceneNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data = []
        for node in nodes:
            data.extend(list(node.center.toTuple()))
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_local_pos_buffer(self, buffer_id: int, nodes: list[SceneNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data = []
        for node in nodes:
            data.extend(list(node._transform._translation.toTuple()))
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_color_buffer(self, buffer_id: int, nodes: list[SceneNode]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        color_data = []
        for node in nodes:
            color_data.extend(list(node.color))
        color_array = np.array(color_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, color_array.nbytes, color_array, GL_STATIC_DRAW)

    def _setup_model_matrix_attributes(self, buffer_id: int, start_index: int):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        # Setup instanced attributes for transformation matrices
        # 4x4 matrix takes 4 attributes (location 2, 3, 4, 5)
        stride = 16 * 4  # 16 floats * 4 bytes per float
        for i in range(4):
            glEnableVertexAttribArray(start_index + i)
            glVertexAttribPointer(start_index + i, 4, GL_FLOAT, False, stride, ctypes.c_void_p(i * 4 * 4))
            glVertexAttribDivisor(start_index + i, 1)  # Updated for each instance

    def _setup_color_attributes(self, buffer_id: int, index: int):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, 4, GL_FLOAT, False, 0, None)
        glVertexAttribDivisor(index, 1)

    def _setup_local_pos_attributes(self, buffer_id: int, index: int):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, 3, GL_FLOAT, False, 0, None)
        glVertexAttribDivisor(index, 1)

    def _setup_center_attributes(self, buffer_id: int, index: int):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        glEnableVertexAttribArray(index)
        glVertexAttribPointer(index, 3, GL_FLOAT, False, 0, None)
        glVertexAttribDivisor(index, 1)

    def _setup_uniforms(self, uniform_locations: UniformLocations):
        view_matrix = self._resource_manager.current_camera.matrix.data()
        scene_matrix = self._resource_manager.current_scene.transform.matrix.data()
        projection_matrix = self._projection_manager.active_projection.matrix.data()

        glUniformMatrix4fv(uniform_locations.view_matrix, 1, False, view_matrix)
        glUniformMatrix4fv(uniform_locations.scene_matrix, 1, False, scene_matrix)
        glUniformMatrix4fv(uniform_locations.projection_matrix, 1, False, projection_matrix)

    def _get_node_depth(self, node: SceneNode) -> float:
        point = QVector3D(0.0, 0.0, 0.0) * node.transform
        return self._resource_manager.current_camera.get_distance_to_point(point)

    def _sort_by_depth(self, nodes: list[SceneNode]) -> list[SceneNode]:
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

        if not transparent_bg:
            image = image.convertToFormat(QImage.Format_RGB32)

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
        for buffer1, buffer2, buffer3, buffer4, _ in self._transformation_buffers.values():
            glDeleteBuffers(1, [buffer1, buffer2, buffer3, buffer4])
