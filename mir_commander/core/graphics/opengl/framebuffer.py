from OpenGL.GL import (
    GL_FRAMEBUFFER,
    GL_FRAMEBUFFER_COMPLETE,
    GL_TEXTURE_2D,
    GL_TEXTURE_2D_MULTISAMPLE,
    glBindFramebuffer,
    glCheckFramebufferStatus,
    glDeleteFramebuffers,
    glFramebufferTexture2D,
    glGenFramebuffers,
)

from .errors import FramebufferError


class Framebuffer:
    def __init__(self):
        self._framebuffer = glGenFramebuffers(1)

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self._framebuffer)

    def attach_texture(self, texture: int, attachment: int, multisample: bool = False):
        textarget = GL_TEXTURE_2D_MULTISAMPLE if multisample else GL_TEXTURE_2D
        glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, textarget, texture, 0)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def check_status(self):
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise FramebufferError(f"Framebuffer `{self._framebuffer}` incomplete: {hex(status)}")

    def release(self):
        glDeleteFramebuffers(1, [self._framebuffer])

    def __repr__(self):
        return f"{self.__class__.__name__}(framebuffer={self._framebuffer})"
