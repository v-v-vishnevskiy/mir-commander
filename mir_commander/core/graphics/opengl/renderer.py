import ctypes
import logging
from enum import Enum
from typing import Hashable, cast

import numpy as np
import OpenGL.error
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_COLOR_ATTACHMENT0,
    GL_DEPTH24_STENCIL8,
    GL_DEPTH_STENCIL_ATTACHMENT,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_LINEAR,
    GL_RENDERBUFFER,
    GL_RGB,
    GL_RGBA,
    GL_STATIC_DRAW,
    GL_TEXTURE0,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TRIANGLES,
    GL_UNSIGNED_BYTE,
    glActiveTexture,
    glBindBuffer,
    glBindFramebuffer,
    glBindRenderbuffer,
    glBindTexture,
    glBufferData,
    glClearColor,
    glDeleteBuffers,
    glDeleteFramebuffers,
    glDeleteRenderbuffers,
    glDeleteTextures,
    glDrawArraysInstanced,
    glEnableVertexAttribArray,
    glFramebufferRenderbuffer,
    glFramebufferTexture2D,
    glGenBuffers,
    glGenFramebuffers,
    glGenRenderbuffers,
    glGenTextures,
    glReadPixels,
    glRenderbufferStorage,
    glTexImage2D,
    glTexParameteri,
    glUniformMatrix4fv,
    glVertexAttribDivisor,
    glVertexAttribPointer,
    glViewport,
)

from mir_commander.core.algebra import Vector3D
from mir_commander.core.graphics.projection import ProjectionManager
from mir_commander.core.graphics.resource_manager import ResourceManager
from mir_commander.core.graphics.scene import Node, NodeType, RenderingContainer, TextNode
from mir_commander.core.graphics.utils import Color4f, crop_image_to_content

from .errors import RendererError
from .shader import UniformLocations
from .wboit import WBOIT

logger = logging.getLogger("Core.Graphics.Renderer")


class PaintMode(Enum):
    Normal = 1
    Picking = 2


class Renderer:
    def __init__(self, projection_manager: ProjectionManager, resource_manager: ResourceManager):
        self._projection_manager = projection_manager
        self._resource_manager = resource_manager
        self._bg_color = (0.0, 0.0, 0.0, 1.0)
        self._picking_image: np.ndarray = np.ndarray([], dtype=np.uint8)
        self._update_picking_image = True
        self._normal_buffers: dict[Hashable, tuple[int, int, int, int, int, int]] = {}
        self._picking_buffers: dict[str, int] = {"color": glGenBuffers(1), "model_matrix": glGenBuffers(1)}
        self._wboit_msaa = WBOIT()
        self._wboit_picking = WBOIT()

        self._device_pixel_ratio = 1.0
        self._width = 1
        self._height = 1
        self._samples = 4

    @property
    def background_color(self) -> Color4f:
        return self._bg_color

    def set_background_color(self, color: Color4f):
        self._bg_color = color

    def resize(self, width: int, height: int, device_pixel_ratio: float):
        self._device_pixel_ratio = device_pixel_ratio
        self._width = width
        self._height = height

        glViewport(0, 0, width, height)
        self._wboit_msaa.init(int(width * device_pixel_ratio), int(height * device_pixel_ratio), self._samples)
        self._wboit_picking.init(width, height, 0)

    def paint(self, paint_mode: PaintMode, framebuffer: int):
        normal_containers, text_rc, picking_rc = self._resource_manager.current_scene.containers

        glClearColor(*self._bg_color)

        if paint_mode == PaintMode.Picking:
            self._wboit_picking.setup()
            self._wboit_picking.prepare_opaque_stage()
            self._paint_picking(picking_rc)
            self._wboit_picking.finalize(framebuffer)
            picking_rc.clear_dirty()
        else:
            self._wboit_msaa.setup()

            self._handle_text(text_rc)

            self._wboit_msaa.prepare_opaque_stage()
            self._paint_normal(normal_containers[NodeType.OPAQUE])

            self._wboit_msaa.prepare_transparent_stage()
            if normal_containers[NodeType.TRANSPARENT]:
                self._paint_normal(normal_containers[NodeType.TRANSPARENT])

            if normal_containers[NodeType.CHAR]:
                self._paint_normal(normal_containers[NodeType.CHAR])

            self._wboit_msaa.finalize(framebuffer)

            for container in normal_containers.values():
                container.clear_dirty()

            self._update_picking_image = True

    def _handle_text(self, text_rc: RenderingContainer[TextNode]):
        for _, nodes in text_rc.batches:
            for node in nodes:
                node.update_char_translation(self._resource_manager.get_font_atlas(node.font_atlas_name))
        text_rc.clear()

    def _paint_picking(self, rc: RenderingContainer[Node]):
        prev_model_name = ""

        self._setup_shader("", "picking")

        for group_id, nodes in rc.batches:
            _, _, model_name = cast(tuple[None, None, str], group_id)

            triangles_count = self._setup_vao(prev_model_name, model_name)
            prev_model_name = model_name

            # Update buffers if needed
            if rc._dirty.get(group_id, False):
                self._update_picking_color_buffer(self._picking_buffers["color"], nodes)
                self._update_model_matrix_buffer(self._picking_buffers["model_matrix"], nodes)
            self._setup_color_attributes(self._picking_buffers["color"], 3)
            self._setup_model_matrix_attributes(self._picking_buffers["model_matrix"], 4)

            glDrawArraysInstanced(GL_TRIANGLES, 0, triangles_count, len(nodes))

    def _paint_normal(self, rc: RenderingContainer[Node]):
        prev_shader_name = ""
        prev_texture_name = ""
        prev_model_name = ""

        for group_id, nodes in rc.batches:
            shader_name, texture_name, model_name = cast(tuple[str, str, str], group_id)

            self._setup_shader(prev_shader_name, shader_name)
            prev_shader_name = shader_name

            prev_texture_name = self._setup_texture(prev_texture_name, texture_name)

            triangles_count = self._setup_vao(prev_model_name, model_name)
            prev_model_name = model_name

            self._setup_instanced_rendering(rc, group_id, nodes)

            # OPTIMIZATION: Single draw call for all instances
            glDrawArraysInstanced(GL_TRIANGLES, 0, triangles_count, len(nodes))

    def _setup_shader(self, prev_shader_name: str, shader_name: str) -> UniformLocations:
        # OPTIMIZATION: Switch shader only when needed (expensive operation)
        shader = self._resource_manager.get_shader(shader_name)
        if shader_name != prev_shader_name:
            shader.use()
            uniform_locations = shader.uniform_locations
            self._setup_uniforms(uniform_locations)
        return shader.uniform_locations

    def _setup_texture(self, prev_texture_name: str, texture_name: str):
        # OPTIMIZATION: Switch texture only when needed (expensive operation)
        if texture_name != "" and texture_name != prev_texture_name:
            texture = self._resource_manager.get_texture(texture_name)
            glActiveTexture(GL_TEXTURE0)
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

    def _setup_instanced_rendering(self, rc: RenderingContainer[Node], group_id: Hashable, nodes: set[Node]):
        # OPTIMIZATION: Use instanced rendering for multiple objects with same geometry
        (
            color_buffer_id,
            model_matrix_buffer_id,
            local_position_buffer_id,
            parent_local_position_buffer_id,
            parent_world_position_buffer_id,
            parent_parent_world_position_buffer_id,
        ) = self._get_normal_buffer(group_id)

        # Update buffers if needed
        if rc._dirty.get(group_id, False):
            self._update_color_buffer(color_buffer_id, nodes)
            self._update_model_matrix_buffer(model_matrix_buffer_id, nodes)
            self._update_local_position_buffer(local_position_buffer_id, nodes)
            self._update_parent_local_position_buffer(parent_local_position_buffer_id, nodes)
            self._update_parent_world_position_buffer(parent_world_position_buffer_id, nodes)
            self._update_parent_parent_world_position_buffer(parent_parent_world_position_buffer_id, nodes)

        # Setup instanced attributes
        self._setup_color_attributes(color_buffer_id, 3)
        self._setup_model_matrix_attributes(model_matrix_buffer_id, 4)
        self._setup_position_attributes(local_position_buffer_id, 8)
        self._setup_position_attributes(parent_local_position_buffer_id, 9)
        self._setup_position_attributes(parent_world_position_buffer_id, 10)
        self._setup_position_attributes(parent_parent_world_position_buffer_id, 11)

    def _get_normal_buffer(self, key: Hashable) -> tuple[int, int, int, int, int, int]:
        if key not in self._normal_buffers:
            self._normal_buffers[key] = (
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
            )
        return self._normal_buffers[key]

    def _update_model_matrix_buffer(self, buffer_id: int, nodes: set[Node]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        transformation_data: list[float] = []
        for node in nodes:
            transformation_data.extend(node.transform.data)
        transformation_array = np.array(transformation_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, transformation_array.nbytes, transformation_array, GL_STATIC_DRAW)

    def _update_local_position_buffer(self, buffer_id: int, nodes: set[Node]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data: list[float] = []
        for node in nodes:
            data.extend(node._transform._position.data)
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_color_buffer(self, buffer_id: int, nodes: set[Node]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        color_data = []
        for node in nodes:
            color_data.extend(list(node.color))
        color_array = np.array(color_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, color_array.nbytes, color_array, GL_STATIC_DRAW)

    def _update_picking_color_buffer(self, buffer_id: int, nodes: set[Node]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        color_data = []
        for node in nodes:
            color_data.extend(list(node.picking_color))
        color_array = np.array(color_data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, color_array.nbytes, color_array, GL_STATIC_DRAW)

    def _update_parent_local_position_buffer(self, buffer_id: int, nodes: set[Node]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data: list[float] = []
        for node in nodes:
            if node._parent is not None:
                data.extend(node._parent._transform._position.data)
            else:
                data.extend([0.0, 0.0, 0.0])
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_parent_world_position_buffer(self, buffer_id: int, nodes: set[Node]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data: list[float] = []
        for node in nodes:
            if node._parent is not None:
                nd = node._parent.transform.data
                center = Vector3D(nd[12], nd[13], nd[14])
                data.extend(center.data)
            else:
                data.extend([0.0, 0.0, 0.0])
        array = np.array(data, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _update_parent_parent_world_position_buffer(self, buffer_id: int, nodes: set[Node]):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        data: list[float] = []
        for node in nodes:
            if node._parent is not None:
                if node._parent._parent is not None:
                    nd = node._parent._parent.transform.data
                    center = Vector3D(nd[12], nd[13], nd[14])
                    data.extend(center.data)
                else:
                    nd = node._parent.transform.data
                    center = Vector3D(nd[12], nd[13], nd[14])
                    data.extend(center.data)
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
        view_matrix = self._resource_manager.current_camera.matrix
        scene_matrix = self._resource_manager.current_scene.transform.matrix
        projection_matrix = self._projection_manager.active_projection.matrix

        glUniformMatrix4fv(uniform_locations.view_matrix, 1, False, view_matrix.data)
        glUniformMatrix4fv(uniform_locations.scene_matrix, 1, False, scene_matrix.data)
        glUniformMatrix4fv(uniform_locations.projection_matrix, 1, False, projection_matrix.data)
        glUniformMatrix4fv(
            uniform_locations.transform_matrix, 1, False, (projection_matrix * view_matrix * scene_matrix).data
        )

    def _render_to_image(self, paint_mode: PaintMode, width: int, height: int, crop_to_content: bool) -> np.ndarray:
        # Create framebuffer
        fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo)

        format = GL_RGBA if self.background_color[3] < 1.0 else GL_RGB
        channels = 4 if self.background_color[3] < 1.0 else 3
        samples = 0 if self.background_color[3] < 1.0 else self._samples

        # Create texture for color attachment
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, format, width, height, 0, format, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

        # Create renderbuffer for depth/stencil
        rbo = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, rbo)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

        # Initialize projections, viewport, and WBOIT for new size
        # TODO: replace with context manager
        self._projection_manager.build_projections(width, height)
        glViewport(0, 0, width, height)
        if paint_mode == PaintMode.Normal:
            self._wboit_msaa.init(width, height, samples)

        # Render scene
        self.paint(paint_mode, fbo)

        # Read pixels from framebuffer
        pixels = glReadPixels(0, 0, width, height, format, GL_UNSIGNED_BYTE)

        # Cleanup
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glDeleteTextures([texture])
        glDeleteRenderbuffers(1, [rbo])
        glDeleteFramebuffers(1, [fbo])

        # Restore projection, viewport, and WBOIT to original size
        self._projection_manager.build_projections(self._width, self._height)
        glViewport(0, 0, self._width, self._height)
        if paint_mode == PaintMode.Normal:
            self._wboit_msaa.init(
                int(self._width * self._device_pixel_ratio), int(self._height * self._device_pixel_ratio), self._samples
            )

        # Convert to numpy array
        opengl_image_data = np.frombuffer(pixels, dtype=np.uint8).reshape(height, width, channels)

        # Flip vertically (OpenGL's origin is bottom-left, image origin is top-left)
        image_data = np.flipud(opengl_image_data)

        if crop_to_content:
            return crop_image_to_content(image_data, self.background_color[0:channels])
        return image_data

    def render_to_image(
        self, width: int, height: int, bg_color: Color4f | None = None, crop_to_content: bool = False
    ) -> np.ndarray:
        try:
            background_color_backup = self.background_color
            if bg_color is not None:
                self.set_background_color(bg_color)

            return self._render_to_image(PaintMode.Normal, width, height, crop_to_content)
        except OpenGL.error.GLError as e:
            raise RendererError(f"Error rendering to image: {e}")
        finally:
            self.set_background_color(background_color_backup)

    def picking_image(self) -> np.ndarray:
        if not self._update_picking_image:
            return self._picking_image

        background_color_backup = self.background_color
        self.set_background_color((0.0, 0.0, 0.0, 1.0))
        try:
            self._picking_image = self._render_to_image(PaintMode.Picking, self._width, self._height, False)
            self._update_picking_image = False
            return self._picking_image
        except OpenGL.error.GLError as e:
            logger.error("Error rendering picking image: %s", e)
            return np.ndarray([], dtype=np.uint8)
        finally:
            self.set_background_color(background_color_backup)

    def release(self):
        self._wboit_msaa.release()
        for buffers in self._normal_buffers.values():
            glDeleteBuffers(1, list(buffers))
        for buffer in self._picking_buffers.values():
            glDeleteBuffers(1, [buffer])
