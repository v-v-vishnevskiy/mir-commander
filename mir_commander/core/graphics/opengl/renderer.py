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
    GL_INT,
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
    glUniform1i,
    glUniformMatrix4fv,
    glVertexAttribDivisor,
    glVertexAttribPointer,
    glViewport,
)

from mir_commander.core.graphics.projection import ProjectionManager
from mir_commander.core.graphics.resource_manager import ResourceManager
from mir_commander.core.graphics.scene.node import Node, NodeType
from mir_commander.core.graphics.scene.rendering_container import RenderingContainer
from mir_commander.core.graphics.scene.text_node import TextNode
from mir_commander.core.graphics.utils import Color4f, crop_image_to_content

from .errors import RendererError
from .shader import FragmentShader, ShaderProgram, UniformLocations, VertexShader
from .wboit import WBOIT

logger = logging.getLogger("Core.Graphics.Renderer")


_COMMON_SHADER_CONSTS = """
const int RENDER_MODE_BILLBOARD = 1;
const int RENDER_MODE_BILLBOARD_TEXT = 2;
const int RENDER_MODE_RAY_CASTING = 3;
const int RAY_CASTING_OBJECT_SPHERE = 1;
"""


VERTEX_SHADER = """
#version 330 core

{_COMMON_SHADER_CONSTS}

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in vec4 instance_color;
layout (location = 4) in int render_mode;
layout (location = 5) in int lighting_model;
layout (location = 6) in int ray_casting_object;
layout (location = 7) in mat4 instance_model_matrix;
layout (location = 11) in vec3 instance_char_local_position;
layout (location = 13) in vec3 instance_text_world_position;

uniform mat4 scene_matrix;
uniform mat4 view_matrix;
uniform mat4 projection_matrix;
uniform mat4 transform_matrix;

out vec3 normal;
out vec4 fragment_color;
out vec2 fragment_texcoord;
flat out int frag_render_mode;
flat out int frag_lighting_model;
flat out int frag_ray_casting_object;

out vec3 sphere_center_view;
out vec3 vertex_pos_view;
out float sphere_radius;

vec3 get_scale(mat4 matrix) {
    vec3 result;
    result.x = length(vec3(matrix[0][0], matrix[0][1], matrix[0][2]));
    result.y = length(vec3(matrix[1][0], matrix[1][1], matrix[1][2]));
    result.z = length(vec3(matrix[2][0], matrix[2][1], matrix[2][2]));
    return result;
}

void billboard_position() {
    // Extract scale from instance model matrix
    vec3 model_scale = get_scale(instance_model_matrix);

    // Extract scale from scene matrix
    vec3 scene_scale = get_scale(scene_matrix);

    vec3 combined_scale = model_scale * scene_scale;

    // Extract billboard center position from instance model matrix
    vec3 billboard_center = vec3(instance_model_matrix[3][0], instance_model_matrix[3][1], instance_model_matrix[3][2]);

    // Transform center to world space
    vec4 world_center = scene_matrix * vec4(billboard_center, 1.0);

    // Transform to view space
    vec4 view_center = view_matrix * world_center;

    // Apply billboard transformation: offset vertex in view space
    // This makes the quad always face the camera
    vec4 view_position = view_center;
    view_position.xyz += position * combined_scale;

    // Project to clip space
    gl_Position = projection_matrix * view_position;

    // For billboard, transform normal from view space back to world space
    // Billboard always faces camera, so we apply inverse view rotation to normals
    mat3 view_rotation = mat3(view_matrix);
    normal = transpose(view_rotation) * in_normal;
}

void billboard_text_position() {
    vec3 view_scale = get_scale(view_matrix);
    vec3 scene_scale = get_scale(scene_matrix);
    vec3 model_scale = get_scale(instance_model_matrix);

    vec3 scale = model_scale * scene_scale * view_scale;

    // Extract billboard center position from instance model matrix
    vec3 billboard_center = instance_text_world_position;

    // Transform center to view space
    vec4 view_center = view_matrix * scene_matrix * vec4(billboard_center, 1.0);

    // Apply billboard transformation: offset vertex in view space
    // This makes the quad always face the camera
    vec4 view_position = view_center;
    view_position.xy += position.xy * scale.xy + instance_char_local_position.xy * scale.xy;

    // Project to clip space
    gl_Position = projection_matrix * view_position;
}

void ray_casting_sphere_position() {
    gl_Position = transform_matrix * instance_model_matrix * vec4(position, 1.0);

    // Extract sphere radius from model matrix (assumes uniform scale)
    float m_radius = length(vec3(instance_model_matrix[0][0], instance_model_matrix[0][1], instance_model_matrix[0][2]));
    float s_radius = length(vec3(scene_matrix[0][0], scene_matrix[0][1], scene_matrix[0][2]));

    sphere_radius = m_radius * s_radius;

    // Transform sphere center to view space
    vec3 sphere_center_world = (scene_matrix * instance_model_matrix * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
    sphere_center_view = (view_matrix * vec4(sphere_center_world, 1.0)).xyz;

    // Transform vertex position to view space
    vec3 vertex_world = (scene_matrix * instance_model_matrix * vec4(position, 1.0)).xyz;
    vertex_pos_view = (view_matrix * vec4(vertex_world, 1.0)).xyz;
}

void normal_position() {
    gl_Position = transform_matrix * instance_model_matrix * vec4(position, 1.0);

    // Transform normal to world space
    normal = mat3(transpose(inverse(scene_matrix * instance_model_matrix))) * in_normal;
}

void main() {
    if (render_mode == RENDER_MODE_BILLBOARD) {
        billboard_position();
    }
    else if (render_mode == RENDER_MODE_BILLBOARD_TEXT) {
        billboard_text_position();
    }
    else if (render_mode == RENDER_MODE_RAY_CASTING) {
        if (ray_casting_object == RAY_CASTING_OBJECT_SPHERE) {
            ray_casting_sphere_position();
        }
        else {
            normal_position();
        }
    }
    else {
        normal_position();
    }

    fragment_color = instance_color;
    fragment_texcoord = vec2(in_texcoord.x, 1.0 - in_texcoord.y);
    frag_render_mode = render_mode;
    frag_lighting_model = lighting_model;
    frag_ray_casting_object = ray_casting_object;
}
""".replace("{_COMMON_SHADER_CONSTS}", _COMMON_SHADER_CONSTS)


FRAGMENT_SHADER = """
#version 330 core

{_COMMON_SHADER_CONSTS}
const int LIGHTING_MODEL_BLINN_PHONG = 1;
const int LIGHTING_MODEL_TEXTURE = 2;

layout (location = 0) out vec4 output_color;
layout (location = 1) out float alpha;

in vec2 fragment_texcoord;
in vec4 fragment_color;
in vec3 normal;
flat in int frag_render_mode;
flat in int frag_lighting_model;
flat in int frag_ray_casting_object;

in vec3 sphere_center_view;
in vec3 vertex_pos_view;
in float sphere_radius;

uniform bool is_picking = false;
uniform bool is_transparent = false;
uniform int ray_casting_object = 0;
uniform sampler2D tex_1;

vec3 ray_casting_sphere() {
    // Ray in view space: from camera (0,0,0) to fragment position
    vec3 ray_origin = vec3(0.0, 0.0, 0.0);
    vec3 ray_dir = normalize(vertex_pos_view);

    // Sphere equation: |P - C|^2 = r^2
    // Ray equation: P = O + t*D
    // Solving: |O + t*D - C|^2 = r^2
    // Let OC = O - C (vector from sphere center to ray origin)
    vec3 oc = ray_origin - sphere_center_view;

    // Quadratic equation: at^2 + bt + c = 0
    float a = dot(ray_dir, ray_dir);
    float b = 2.0 * dot(oc, ray_dir);
    float c = dot(oc, oc) - sphere_radius * sphere_radius;

    float discriminant = b*b - 4.0*a*c;

    // No intersection - discard fragment
    if (discriminant < 0.0) {
        discard;
    }

    // Find nearest intersection
    float t = (-b - sqrt(discriminant)) / (2.0 * a);

    // If intersection is behind the camera, discard
    if (t < 0.0) {
        discard;
    }

    // Calculate intersection point in view space
    return ray_origin + ray_dir * t;
}

vec4 blinn_phong(vec3 norm, float shininess) {
    const float Pi = 3.14159265;
    vec3 light_color = vec3(1.0, 1.0, 1.0) * 0.9;
    vec3 light_pos = vec3(0.3, 0.3, 1.0);
    vec3 light_dir = normalize(light_pos);

    // Ambient
    float ambient_strength = 0.3;
    vec3 ambient = light_color * ambient_strength;

    // Diffuse
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * light_color;

    // Specular
    float specular_strength = 0.6;

    float energy_conservation = ( 8.0 + shininess ) / ( 8.0 * Pi );
    float spec = energy_conservation * pow(max(dot(norm, light_dir), 0.0), shininess);

    vec3 specular = specular_strength * spec * light_color;

    vec3 final_color = ((ambient + diffuse) * fragment_color.xyz) + specular;
    return vec4(final_color, fragment_color.w);
}

vec4 get_color(vec3 norm, float shininess) {
    vec4 color = fragment_color;

    if (frag_lighting_model == LIGHTING_MODEL_BLINN_PHONG) {
        color = blinn_phong(norm, shininess);
    }
    else if (frag_lighting_model == LIGHTING_MODEL_TEXTURE) {
        vec4 tex_color = texture(tex_1, fragment_texcoord);
        if (tex_color.a < 0.01) {
            discard;
        }
        color *= tex_color;
    }

    return color;
}

void main() {
    vec3 norm = vec3(0.0, 0.0, 0.0);
    if (frag_render_mode == RENDER_MODE_RAY_CASTING) {
        if (frag_ray_casting_object == RAY_CASTING_OBJECT_SPHERE) {
            norm = normalize(ray_casting_sphere() - sphere_center_view);
        }
        else {
            norm = normalize(normal);
        }
    }
    else {
        norm = normalize(normal);
    }

    if (is_picking) {
        output_color = fragment_color;
    }
    else if (is_transparent) {
        vec4 color = get_color(norm, 32.0);
        output_color = vec4(color.rgb * color.a, color.a);
        alpha = 1.0 - color.a;
    }
    else {
        output_color = get_color(norm, 16.0);
    }
}
""".replace("{_COMMON_SHADER_CONSTS}", _COMMON_SHADER_CONSTS)


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
        self._buffers: dict[Hashable, tuple[int, int, int, int, int, int, int, int, int]] = {}
        self._wboit_msaa = WBOIT()
        self._wboit_picking = WBOIT()
        self._resource_manager.add_shader(
            "default", ShaderProgram(VertexShader(VERTEX_SHADER), FragmentShader(FRAGMENT_SHADER))
        )

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
            self._paint_normal(normal_containers[NodeType.OPAQUE], False)

            self._wboit_msaa.prepare_transparent_stage()
            if normal_containers[NodeType.TRANSPARENT]:
                self._paint_normal(normal_containers[NodeType.TRANSPARENT], True)

            if normal_containers[NodeType.CHAR]:
                self._paint_normal(normal_containers[NodeType.CHAR], True)

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

        self._setup_shader("", "default", False, True)

        for group_id, nodes in rc.batches:
            _, _, model_name = cast(tuple[None, None, str], group_id)

            triangles_count = self._setup_vao(prev_model_name, model_name)
            prev_model_name = model_name

            self._setup_instanced_rendering(rc, group_id, nodes, False, True)

            glDrawArraysInstanced(GL_TRIANGLES, 0, triangles_count, len(nodes))

    def _paint_normal(self, rc: RenderingContainer[Node], is_transparent: bool):
        prev_shader_name = ""
        prev_texture_name = ""
        prev_model_name = ""

        for group_id, nodes in rc.batches:
            shader_name, texture_name, model_name = cast(tuple[str, str, str], group_id)

            shader_name = shader_name or "default"
            self._setup_shader(prev_shader_name, shader_name, is_transparent, False)
            prev_shader_name = shader_name

            prev_texture_name = self._setup_texture(prev_texture_name, texture_name)

            triangles_count = self._setup_vao(prev_model_name, model_name)
            prev_model_name = model_name

            self._setup_instanced_rendering(rc, group_id, nodes, is_transparent, False)

            # OPTIMIZATION: Single draw call for all instances
            glDrawArraysInstanced(GL_TRIANGLES, 0, triangles_count, len(nodes))

    def _setup_shader(
        self, prev_shader_name: str, shader_name: str, is_transparent: bool, is_picking: bool
    ) -> UniformLocations:
        # OPTIMIZATION: Switch shader only when needed (expensive operation)
        shader = self._resource_manager.get_shader(shader_name)
        if shader_name != prev_shader_name:
            shader.use()
            self._setup_uniforms(shader.uniform_locations, is_transparent, is_picking)
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

    def _setup_instanced_rendering(
        self, rc: RenderingContainer[Node], group_id: Hashable, nodes: set[Node], is_transparent: bool, is_picking: bool
    ):
        # OPTIMIZATION: Use instanced rendering for multiple objects with same geometry
        buffer_ids = self._get_normal_buffer((group_id, is_transparent, is_picking))

        collect_data = rc._dirty.get(group_id, False)

        data = self._prepare_data(nodes, is_picking, collect_data, *buffer_ids)

        # Update buffers if needed
        if collect_data:
            self._update_buffers(data)

        # Setup instanced attributes
        self._setup_attributes(data)

    def _get_normal_buffer(self, key: Hashable) -> tuple[int, int, int, int, int, int, int, int, int]:
        if key not in self._buffers:
            self._buffers[key] = (
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
                glGenBuffers(1),
            )
        return self._buffers[key]

    def _prepare_data(
        self,
        nodes: set[Node],
        is_picking: bool,
        collect_data: bool,
        color_buffer_id: int,
        render_mode_buffer_id: int,
        lighting_model_buffer_id: int,
        ray_casting_object_buffer_id: int,
        model_matrix_buffer_id: int,
        local_position_buffer_id: int,
        parent_local_position_buffer_id: int,
        parent_world_position_buffer_id: int,
        parent_parent_world_position_buffer_id: int,
    ) -> list[tuple[int, np.ndarray, int, int, int, bool]]:
        transformation_data: list[float] = []
        local_position_data: list[float] = []
        color_data: list[float] = []
        render_mode_data: list[int] = []
        lighting_model_data: list[int] = []
        ray_casting_object_data: list[int] = []
        parent_local_position_data: list[float] = []
        parent_world_position_data: list[float] = []
        parent_parent_world_position_data: list[float] = []
        if collect_data:
            for node in nodes:
                transformation_data.extend(node.transform_matrix.data)
                local_position_data.extend(node.transform.position.data)
                color_data.extend(list(node.picking_color if is_picking else node.color))
                render_mode_data.append(node.shader_params.get("render_mode", 0))
                lighting_model_data.append(node.shader_params.get("lighting_model", 0))
                ray_casting_object_data.append(node.shader_params.get("ray_casting_object", 0))

                if node._parent is not None:
                    parent_local_position_data.extend(node._parent.transform.position.data)
                else:
                    parent_local_position_data.extend([0.0, 0.0, 0.0])

                if node._parent is not None:
                    nd = node._parent.transform_matrix.data
                    parent_world_position_data.extend((nd[12], nd[13], nd[14]))
                else:
                    parent_world_position_data.extend([0.0, 0.0, 0.0])

                if node._parent is not None:
                    if node._parent._parent is not None:
                        nd = node._parent._parent.transform_matrix.data
                        parent_parent_world_position_data.extend((nd[12], nd[13], nd[14]))
                    else:
                        nd = node._parent.transform_matrix.data
                        parent_parent_world_position_data.extend((nd[12], nd[13], nd[14]))
                else:
                    parent_parent_world_position_data.extend([0.0, 0.0, 0.0])

        return [
            (color_buffer_id, np.array(color_data, dtype=np.float32), 3, 4, GL_FLOAT, False),
            (render_mode_buffer_id, np.array(render_mode_data, dtype=np.int32), 4, 1, GL_INT, False),
            (lighting_model_buffer_id, np.array(lighting_model_data, dtype=np.int32), 5, 1, GL_INT, False),
            (ray_casting_object_buffer_id, np.array(ray_casting_object_data, dtype=np.int32), 6, 1, GL_INT, False),
            (model_matrix_buffer_id, np.array(transformation_data, dtype=np.float32), 7, 4, GL_FLOAT, True),
            (local_position_buffer_id, np.array(local_position_data, dtype=np.float32), 11, 3, GL_FLOAT, False),
            (
                parent_local_position_buffer_id,
                np.array(parent_local_position_data, dtype=np.float32),
                12,
                3,
                GL_FLOAT,
                False,
            ),
            (
                parent_world_position_buffer_id,
                np.array(parent_world_position_data, dtype=np.float32),
                13,
                3,
                GL_FLOAT,
                False,
            ),
            (
                parent_parent_world_position_buffer_id,
                np.array(parent_parent_world_position_data, dtype=np.float32),
                14,
                3,
                GL_FLOAT,
                False,
            ),
        ]

    def _update_buffers(self, data: list[tuple[int, np.ndarray, int, int, int, bool]]):
        for buffer_id, array, _, _, _, _ in data:
            glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
            glBufferData(GL_ARRAY_BUFFER, array.nbytes, array, GL_STATIC_DRAW)

    def _setup_attributes(self, data: list[tuple[int, np.ndarray, int, int, int, bool]]):
        for buffer_id, _, index, size, type, matrix in data:
            self._setup_buffer_attributes(buffer_id, index, size, type, matrix)

    def _setup_buffer_attributes(self, buffer_id: int, index: int, size: int, type: int, matrix: bool = False):
        glBindBuffer(GL_ARRAY_BUFFER, buffer_id)
        if matrix:
            stride = 16 * 4  # 16 floats * 4 bytes per float
            for i in range(4):
                glEnableVertexAttribArray(index + i)
                glVertexAttribPointer(index + i, size, type, False, stride, ctypes.c_void_p(i * 4 * 4))
                glVertexAttribDivisor(index + i, 1)  # Updated for each instance
        else:
            glEnableVertexAttribArray(index)
            glVertexAttribPointer(index, size, type, False, 0, None)
            glVertexAttribDivisor(index, 1)

    def _setup_uniforms(self, uniform_locations: UniformLocations, is_transparent: bool, is_picking: bool):
        view_matrix = self._resource_manager.current_camera.matrix
        scene_matrix = self._resource_manager.current_scene.transform.matrix
        projection_matrix = self._projection_manager.active_projection.matrix

        glUniformMatrix4fv(uniform_locations.view_matrix, 1, False, view_matrix.data)
        glUniformMatrix4fv(uniform_locations.scene_matrix, 1, False, scene_matrix.data)
        glUniformMatrix4fv(uniform_locations.projection_matrix, 1, False, projection_matrix.data)
        glUniformMatrix4fv(
            uniform_locations.transform_matrix, 1, False, (projection_matrix * view_matrix * scene_matrix).data
        )
        glUniform1i(uniform_locations.is_transparent, is_transparent)
        glUniform1i(uniform_locations.is_picking, is_picking)

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
        self._wboit_picking.release()
        for buffers in self._buffers.values():
            glDeleteBuffers(1, list(buffers))
