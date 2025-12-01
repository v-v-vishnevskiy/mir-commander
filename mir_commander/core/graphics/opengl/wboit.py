from OpenGL.GL import (
    GL_BACK,
    GL_BLEND,
    GL_COLOR,
    GL_COLOR_ATTACHMENT0,
    GL_COLOR_ATTACHMENT1,
    GL_COLOR_BUFFER_BIT,
    GL_CULL_FACE,
    GL_DEPTH_ATTACHMENT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_COMPONENT,
    GL_DEPTH_TEST,
    GL_DRAW_FRAMEBUFFER,
    GL_DST_COLOR,
    GL_FALSE,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_FUNC_ADD,
    GL_HALF_FLOAT,
    GL_LEQUAL,
    GL_LESS,
    GL_LINEAR,
    GL_MULTISAMPLE,
    GL_ONE,
    GL_R16F,
    GL_READ_FRAMEBUFFER,
    GL_RED,
    GL_RGBA,
    GL_RGBA16F,
    GL_SAMPLE_SHADING,
    GL_TEXTURE0,
    GL_TEXTURE1,
    GL_TEXTURE2,
    GL_TRIANGLES,
    GL_TRUE,
    GL_ZERO,
    glActiveTexture,
    glBindFramebuffer,
    glBlendEquationi,
    glBlendFunci,
    glBlitFramebuffer,
    glClear,
    glClearBufferfv,
    glCullFace,
    glDepthFunc,
    glDepthMask,
    glDisable,
    glDrawArrays,
    glDrawBuffer,
    glDrawBuffers,
    glEnable,
    glGetUniformLocation,
    glMinSampleShading,
    glReadBuffer,
    glUniform1i,
)

from mir_commander.core.graphics.mesh import rect

from .framebuffer import Framebuffer
from .shader import FragmentShader, ShaderProgram, VertexShader
from .texture2d import Texture2D
from .vertex_array_object import VertexArrayObject

VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec3 position;
layout (location = 2) in vec2 in_texcoord;

out vec2 fragment_texcoord;

void main() {
    gl_Position = vec4(position.xy, 0.0, 1.0);
    fragment_texcoord = in_texcoord;
}
"""


FRAGMENT_SHADER = """
#version 330 core

in vec2 fragment_texcoord;
uniform sampler2D opaque_texture;
uniform sampler2D accum_texture;
uniform sampler2D alpha_texture;

out vec4 output_color;

void main() {
    vec4 opaque_color = texture(opaque_texture, fragment_texcoord);
    vec4 accum = texture(accum_texture, fragment_texcoord);
    float alpha = 1.0 - texture(alpha_texture, fragment_texcoord).r;

    // If no transparent geometry, show opaque only
    if (accum.a <= 0.0001) {
        output_color = opaque_color;
        return;
    }

    // Compute average transparent color
    vec3 transparent_color = accum.rgb / accum.a;

    // Output alpha depends on background type
    float output_alpha = opaque_color.a > 0.0 ? max(alpha, opaque_color.a) : alpha;

    // Blend with opaque background if present, otherwise output straight alpha
    vec3 color;
    if (opaque_color.a > 0.0) {
        // Blend transparent over opaque background
        color = transparent_color * alpha + opaque_color.rgb * (1.0 - alpha);
    } else {
        // No opaque background - output straight alpha (not premultiplied)
        color = transparent_color;
    }

    output_color = vec4(color, output_alpha);
}
"""


class WBOIT:
    def __init__(self):
        self._opaque_fbo = Framebuffer()
        self._transparent_fbo = Framebuffer()
        self._opaque_resolve_fbo = Framebuffer()
        self._transparent_resolve_fbo = Framebuffer()

        self._opaque_texture = Texture2D()
        self._depth_texture = Texture2D()
        self._accum_texture = Texture2D()
        self._alpha_texture = Texture2D()

        self._opaque_resolve_texture = Texture2D()
        self._accum_resolve_texture = Texture2D()
        self._alpha_resolve_texture = Texture2D()

        self._fullscreen_quad_vao = VertexArrayObject(
            rect.get_vertices(), rect.get_normals(), rect.get_texture_coords()
        )

        self._finalize_shader = ShaderProgram(VertexShader(VERTEX_SHADER), FragmentShader(FRAGMENT_SHADER))

        self._opaque_texture_loc = glGetUniformLocation(self._finalize_shader.program, "opaque_texture")
        self._accum_texture_loc = glGetUniformLocation(self._finalize_shader.program, "accum_texture")
        self._alpha_texture_loc = glGetUniformLocation(self._finalize_shader.program, "alpha_texture")

        self._samples = 0
        self._width = 0
        self._height = 0

    def init(self, width: int, height: int, samples: int = 0):
        self._samples = samples
        self._width = width
        self._height = height

        # Create multisampled textures for rendering
        self._opaque_texture.init(width, height, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT, samples=samples)
        self._depth_texture.init(
            width, height, GL_DEPTH_COMPONENT, GL_DEPTH_COMPONENT, GL_FLOAT, None, False, samples=samples
        )
        self._accum_texture.init(width, height, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT, samples=samples)
        self._alpha_texture.init(width, height, GL_R16F, GL_RED, GL_HALF_FLOAT, samples=samples)

        self._opaque_fbo.bind()
        self._opaque_fbo.attach_texture(self._opaque_texture.id, GL_COLOR_ATTACHMENT0, multisample=samples > 0)
        self._opaque_fbo.attach_texture(self._depth_texture.id, GL_DEPTH_ATTACHMENT, multisample=samples > 0)
        self._opaque_fbo.check_status()
        self._opaque_fbo.unbind()

        self._transparent_fbo.bind()
        self._transparent_fbo.attach_texture(self._accum_texture.id, GL_COLOR_ATTACHMENT0, multisample=samples > 0)
        self._transparent_fbo.attach_texture(self._alpha_texture.id, GL_COLOR_ATTACHMENT1, multisample=samples > 0)
        self._transparent_fbo.attach_texture(self._depth_texture.id, GL_DEPTH_ATTACHMENT, multisample=samples > 0)
        self._transparent_fbo.check_status()
        glDrawBuffers(2, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1])
        self._transparent_fbo.unbind()

        # Create resolve textures (non-multisampled) for finalization
        if samples > 0:
            self._opaque_resolve_texture.init(width, height, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT, samples=0)
            self._accum_resolve_texture.init(width, height, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT, samples=0)
            self._alpha_resolve_texture.init(width, height, GL_R16F, GL_RED, GL_HALF_FLOAT, samples=0)

            self._opaque_resolve_fbo.bind()
            self._opaque_resolve_fbo.attach_texture(self._opaque_resolve_texture.id, GL_COLOR_ATTACHMENT0)
            self._opaque_resolve_fbo.check_status()
            self._opaque_resolve_fbo.unbind()

            self._transparent_resolve_fbo.bind()
            self._transparent_resolve_fbo.attach_texture(self._accum_resolve_texture.id, GL_COLOR_ATTACHMENT0)
            self._transparent_resolve_fbo.attach_texture(self._alpha_resolve_texture.id, GL_COLOR_ATTACHMENT1)
            self._transparent_resolve_fbo.check_status()
            glDrawBuffers(2, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1])
            self._transparent_resolve_fbo.unbind()

    def setup(self):
        if self._samples > 0:
            glEnable(GL_MULTISAMPLE)
            glEnable(GL_SAMPLE_SHADING)
            glMinSampleShading(1.0)
        else:
            glDisable(GL_MULTISAMPLE)
            glDisable(GL_SAMPLE_SHADING)

    def prepare_opaque_stage(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glDepthFunc(GL_LESS)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glCullFace(GL_BACK)

        self._opaque_fbo.bind()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def prepare_transparent_stage(self):
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunci(0, GL_ONE, GL_ONE)
        glBlendEquationi(0, GL_FUNC_ADD)
        glBlendFunci(1, GL_DST_COLOR, GL_ZERO)
        glBlendEquationi(1, GL_FUNC_ADD)

        self._transparent_fbo.bind()
        glClearBufferfv(GL_COLOR, 0, [0.0, 0.0, 0.0, 0.0])
        glClearBufferfv(GL_COLOR, 1, [1.0])

    def finalize(self, framebuffer: int):
        # Resolve multisampled textures if needed
        if self._samples > 0:
            self._resolve_multisampled_textures()

        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._finalize_shader.use()

        # Bind appropriate textures based on multisampling
        if self._samples > 0:
            glActiveTexture(GL_TEXTURE0)
            self._opaque_resolve_texture.bind()
            glUniform1i(self._opaque_texture_loc, 0)

            glActiveTexture(GL_TEXTURE1)
            self._accum_resolve_texture.bind()
            glUniform1i(self._accum_texture_loc, 1)

            glActiveTexture(GL_TEXTURE2)
            self._alpha_resolve_texture.bind()
            glUniform1i(self._alpha_texture_loc, 2)
        else:
            glActiveTexture(GL_TEXTURE0)
            self._opaque_texture.bind()
            glUniform1i(self._opaque_texture_loc, 0)

            glActiveTexture(GL_TEXTURE1)
            self._accum_texture.bind()
            glUniform1i(self._accum_texture_loc, 1)

            glActiveTexture(GL_TEXTURE2)
            self._alpha_texture.bind()
            glUniform1i(self._alpha_texture_loc, 2)

        self._fullscreen_quad_vao.bind()
        glDrawArrays(GL_TRIANGLES, 0, self._fullscreen_quad_vao.triangles_count)

    def _resolve_multisampled_textures(self):
        # Blit opaque texture
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self._opaque_fbo._framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self._opaque_resolve_fbo._framebuffer)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)
        glBlitFramebuffer(
            0, 0, self._width, self._height, 0, 0, self._width, self._height, GL_COLOR_BUFFER_BIT, GL_LINEAR
        )

        # Blit transparent textures - need to blit each attachment separately
        glBindFramebuffer(GL_READ_FRAMEBUFFER, self._transparent_fbo._framebuffer)
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self._transparent_resolve_fbo._framebuffer)

        # Blit accum texture (COLOR_ATTACHMENT0)
        glReadBuffer(GL_COLOR_ATTACHMENT0)
        glDrawBuffer(GL_COLOR_ATTACHMENT0)
        glBlitFramebuffer(
            0, 0, self._width, self._height, 0, 0, self._width, self._height, GL_COLOR_BUFFER_BIT, GL_LINEAR
        )

        # Blit alpha texture (COLOR_ATTACHMENT1)
        glReadBuffer(GL_COLOR_ATTACHMENT1)
        glDrawBuffer(GL_COLOR_ATTACHMENT1)
        glBlitFramebuffer(
            0, 0, self._width, self._height, 0, 0, self._width, self._height, GL_COLOR_BUFFER_BIT, GL_LINEAR
        )

    def release(self):
        self._opaque_fbo.release()
        self._transparent_fbo.release()

        self._opaque_texture.release()
        self._depth_texture.release()
        self._accum_texture.release()
        self._alpha_texture.release()

        if self._samples > 0:
            self._opaque_resolve_fbo.release()
            self._transparent_resolve_fbo.release()
            self._opaque_resolve_texture.release()
            self._accum_resolve_texture.release()
            self._alpha_resolve_texture.release()

        self._fullscreen_quad_vao.release()

        self._finalize_shader.release()
