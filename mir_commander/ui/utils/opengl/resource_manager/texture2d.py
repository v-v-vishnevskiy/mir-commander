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

logger = logging.getLogger("ResourceManager.Texture2D")


class Texture2D(Resource):
    def __init__(self, name: str, width: int, height: int, data: np.ndarray):
        super().__init__(name)

        self._texture = None

        self._load(width, height, data)

    def _load(self, width: int, height: int, data: np.ndarray):
        logger.debug(f"Loading texture {self.name}")

        self.unbind()

        self._texture = glGenTextures(1)
        self.bind()

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self._texture)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)

    def __del__(self):
        glDeleteTextures(1, [self._texture])

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, texture={self._texture})"
