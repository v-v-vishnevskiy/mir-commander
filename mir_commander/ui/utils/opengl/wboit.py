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
    GL_DST_COLOR,
    GL_FALSE,
    GL_FLOAT,
    GL_FRAMEBUFFER,
    GL_FUNC_ADD,
    GL_HALF_FLOAT,
    GL_LEQUAL,
    GL_LESS,
    GL_ONE,
    GL_R16F,
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
    glClear,
    glClearBufferfv,
    glCullFace,
    glDepthFunc,
    glDepthMask,
    glDisable,
    glDrawArrays,
    glDrawBuffers,
    glEnable,
    glGetUniformLocation,
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

        self._opaque_texture = Texture2D("wboit_opaque_texture")
        self._depth_texture = Texture2D("wboit_depth_texture")
        self._accum_texture = Texture2D("wboit_accum_texture")
        self._alpha_texture = Texture2D("wboit_alpha_texture")

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

    def init(self, width: int, height: int):
        self._opaque_texture.init(width, height, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT)
        self._depth_texture.init(width, height, GL_DEPTH_COMPONENT, GL_DEPTH_COMPONENT, GL_FLOAT, None, False)
        self._accum_texture.init(width, height, GL_RGBA16F, GL_RGBA, GL_HALF_FLOAT)
        self._alpha_texture.init(width, height, GL_R16F, GL_RED, GL_HALF_FLOAT)

        self._opaque_fbo.bind()
        self._opaque_fbo.attach_texture(self._opaque_texture.id, GL_COLOR_ATTACHMENT0)
        self._opaque_fbo.attach_texture(self._depth_texture.id, GL_DEPTH_ATTACHMENT)
        self._opaque_fbo.check_status()
        self._opaque_fbo.unbind()

        self._transparent_fbo.bind()
        self._transparent_fbo.attach_texture(self._accum_texture.id, GL_COLOR_ATTACHMENT0)
        self._transparent_fbo.attach_texture(self._alpha_texture.id, GL_COLOR_ATTACHMENT1)
        self._transparent_fbo.attach_texture(self._depth_texture.id, GL_DEPTH_ATTACHMENT)
        self._transparent_fbo.check_status()
        glDrawBuffers(2, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1])
        self._transparent_fbo.unbind()

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
        glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self._finalize_shader.use()

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

    def release(self):
        self._opaque_fbo.release()
        self._transparent_fbo.release()

        self._opaque_texture.release()
        self._depth_texture.release()
        self._accum_texture.release()
        self._alpha_texture.release()

        self._fullscreen_quad_vao.release()

        self._finalize_shader.release()
