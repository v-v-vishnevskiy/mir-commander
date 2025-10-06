import logging

from OpenGL.GL import (
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
    GL_FRAMEBUFFER_COMPLETE,
    GL_FUNC_ADD,
    GL_HALF_FLOAT,
    GL_LEQUAL,
    GL_LESS,
    GL_LINEAR,
    GL_ONE,
    GL_R16F,
    GL_RED,
    GL_RGBA,
    GL_RGBA16F,
    GL_TEXTURE0,
    GL_TEXTURE1,
    GL_TEXTURE2,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TRIANGLES,
    GL_TRUE,
    GL_ZERO,
    glActiveTexture,
    glBindFramebuffer,
    glBindTexture,
    glBlendEquationi,
    glBlendFunci,
    glCheckFramebufferStatus,
    glClear,
    glClearBufferfv,
    glDeleteFramebuffers,
    glDeleteProgram,
    glDeleteTextures,
    glDepthFunc,
    glDepthMask,
    glDisable,
    glDrawArrays,
    glDrawBuffers,
    glEnable,
    glFramebufferTexture2D,
    glGenFramebuffers,
    glGenTextures,
    glGetUniformLocation,
    glTexImage2D,
    glTexParameteri,
    glUniform1i,
    glUseProgram,
)

from . import shaders
from .models import rect
from .resource_manager import (
    FragmentShader,
    ShaderProgram,
    VertexArrayObject,
    VertexShader,
)

logger = logging.getLogger("OpenGL.WBOIT")


class WBOIT:
    def __init__(self):
        self._default_fbo = 0

        self._opaque_fbo = glGenFramebuffers(1)
        self._opaque_texture = glGenTextures(1)
        self._depth_texture = glGenTextures(1)

        self._transparent_fbo = glGenFramebuffers(1)
        self._accum_texture = glGenTextures(1)
        self._alpha_texture = glGenTextures(1)

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

    def init(self, width: int, height: int, default_fbo: int):
        self._default_fbo = default_fbo

        glBindTexture(GL_TEXTURE_2D, self._opaque_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, width, height, 0, GL_RGBA, GL_HALF_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        glBindTexture(GL_TEXTURE_2D, self._depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, width, height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glBindTexture(GL_TEXTURE_2D, 0)

        glBindFramebuffer(GL_FRAMEBUFFER, self._opaque_fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._opaque_texture, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self._depth_texture, 0)

        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            logger.error(f"Opaque framebuffer incomplete: {hex(status)}")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        glBindTexture(GL_TEXTURE_2D, self._accum_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, width, height, 0, GL_RGBA, GL_HALF_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        glBindTexture(GL_TEXTURE_2D, self._alpha_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R16F, width, height, 0, GL_RED, GL_HALF_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        glBindFramebuffer(GL_FRAMEBUFFER, self._transparent_fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self._accum_texture, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, self._alpha_texture, 0)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self._depth_texture, 0)
        glDrawBuffers(2, [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1])

        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            logger.error(f"Transparent framebuffer incomplete: {hex(status)}")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def prepare_opaque_stage(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        glBindFramebuffer(GL_FRAMEBUFFER, self._opaque_fbo)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def prepare_transparent_stage(self):
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunci(0, GL_ONE, GL_ONE)
        glBlendEquationi(0, GL_FUNC_ADD)
        # glBlendFunci(1, GL_ZERO, GL_ONE_MINUS_SRC_COLOR)
        glBlendFunci(1, GL_DST_COLOR, GL_ZERO)
        glBlendEquationi(1, GL_FUNC_ADD)

        glBindFramebuffer(GL_FRAMEBUFFER, self._transparent_fbo)
        glClearBufferfv(GL_COLOR, 0, [0.0, 0.0, 0.0, 0.0])
        glClearBufferfv(GL_COLOR, 1, [1.0])

    def finalize(self):
        # glDisable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        glBindFramebuffer(GL_FRAMEBUFFER, self._default_fbo)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(self._finalize_shader.program)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self._opaque_texture)
        glUniform1i(self._opaque_texture_loc, 0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self._accum_texture)
        glUniform1i(self._accum_texture_loc, 1)

        glActiveTexture(GL_TEXTURE2)
        glBindTexture(GL_TEXTURE_2D, self._alpha_texture)
        glUniform1i(self._alpha_texture_loc, 2)

        self._fullscreen_quad_vao.bind()
        glDrawArrays(GL_TRIANGLES, 0, self._fullscreen_quad_vao.triangles_count)

    def release(self):
        glDeleteFramebuffers(1, [self._opaque_fbo])
        glDeleteTextures(1, [self._opaque_texture, self._depth_texture])
        glDeleteFramebuffers(1, [self._transparent_fbo])
        glDeleteTextures(1, [self._accum_texture, self._alpha_texture])
        glDeleteProgram(self._finalize_shader.program)

    def __del__(self):
        self.release()
