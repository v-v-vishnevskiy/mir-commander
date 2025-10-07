import logging

from OpenGL.GL import (
    GL_FRAMEBUFFER,
    GL_FRAMEBUFFER_COMPLETE,
    GL_TEXTURE_2D,
    glBindFramebuffer,
    glCheckFramebufferStatus,
    glDeleteFramebuffers,
    glFramebufferTexture2D,
    glGenFramebuffers,
)

from .base import Resource
from .texture2d import Texture2D

logger = logging.getLogger("OpenGL.Framebuffer")


class Framebuffer(Resource):
    def __init__(self, name: str):
        super().__init__(name)

        self._framebuffer = glGenFramebuffers(1)

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self._framebuffer)

    def attach_texture(self, texture: Texture2D, attachment: int):
        glFramebufferTexture2D(GL_FRAMEBUFFER, attachment, GL_TEXTURE_2D, texture.id, 0)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def check_status(self):
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            logger.error("Framebuffer `%s` incomplete: %s", self.name, hex(status))

    def release(self):
        logger.debug("Deleting resources: %s", self.name)

        glDeleteFramebuffers(1, [self._framebuffer])

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, framebuffer={self._framebuffer})"
