import logging

import numpy as np
from OpenGL.GL import (
    GL_LINEAR,
    GL_RGBA,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glDeleteTextures,
    glGenTextures,
    glTexImage2D,
    glTexParameteri,
)

from .base import Resource

logger = logging.getLogger("OpenGL.Texture2D")


class Texture2D(Resource):
    def __init__(self, name: str):
        super().__init__(name)
        self._texture = glGenTextures(1)

    @property
    def id(self) -> int:
        return self._texture

    def init(
        self,
        width: int,
        height: int,
        internal_format: int = GL_RGBA,
        format: int = GL_RGBA,
        type: int = GL_UNSIGNED_BYTE,
        data: np.ndarray | None = None,
        setup_parameters: bool = True,
    ):
        self.bind()
        glTexImage2D(GL_TEXTURE_2D, 0, internal_format, width, height, 0, format, type, data)
        if setup_parameters:
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        self.unbind()

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self._texture)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def release(self):
        logger.debug("Deleting resources: %s", self.name)

        glDeleteTextures(1, [self._texture])

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, texture={self._texture})"
