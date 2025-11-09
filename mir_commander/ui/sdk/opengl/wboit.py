import logging

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
    glReadBuffer,
    glUniform1i,
)

from . import shaders
from .models import rect
from .resource_manager import (
    FragmentShader,
    Framebuffer,
    ShaderProgram,
    Texture2D,
    VertexArrayObject,
    VertexShader,
)

logger = logging.getLogger("OpenGL.WBOIT")


class WBOIT:
    def __init__(self):
        self._opaque_fbo = Framebuffer("wboit_opaque_fbo")
        self._transparent_fbo = Framebuffer("wboit_transparent_fbo")
        self._opaque_resolve_fbo = Framebuffer("wboit_opaque_resolve_fbo")
        self._transparent_resolve_fbo = Framebuffer("wboit_transparent_resolve_fbo")

        self._opaque_texture = Texture2D("wboit_opaque_texture")
        self._depth_texture = Texture2D("wboit_depth_texture")
        self._accum_texture = Texture2D("wboit_accum_texture")
        self._alpha_texture = Texture2D("wboit_alpha_texture")

        self._opaque_resolve_texture = Texture2D("wboit_opaque_resolve_texture")
        self._accum_resolve_texture = Texture2D("wboit_accum_resolve_texture")
        self._alpha_resolve_texture = Texture2D("wboit_alpha_resolve_texture")

        self._fullscreen_quad_vao = VertexArrayObject(
            "wboit_fullscreen_quad", rect.get_vertices(), rect.get_normals(), rect.get_texture_coords()
        )

        self._finalize_shader = ShaderProgram(
            "wboit_finalize",
            VertexShader(shaders.vertex.WBOIT_FINALIZE),
            FragmentShader(shaders.fragment.WBOIT_FINALIZE),
        )

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
        else:
            glDisable(GL_MULTISAMPLE)

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
