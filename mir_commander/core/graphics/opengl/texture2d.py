import numpy as np
from OpenGL.GL import (
    GL_CLAMP_TO_EDGE,
    GL_LINEAR,
    GL_LINEAR_MIPMAP_LINEAR,
    GL_RGBA,
    GL_TEXTURE_2D,
    GL_TEXTURE_2D_MULTISAMPLE,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glDeleteTextures,
    glGenerateMipmap,
    glGenTextures,
    glTexImage2D,
    glTexImage2DMultisample,
    glTexParameteri,
)


class Texture2D:
    def __init__(self):
        self._texture = glGenTextures(1)
        self._samples = 0

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
        use_mipmaps: bool = False,
        samples: int = 0,
    ):
        if self._samples != samples:
            glDeleteTextures(1, [self._texture])
            self._texture = glGenTextures(1)
        self._samples = samples
        self.bind()
        if self._samples > 0:
            glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, self._samples, internal_format, width, height, True)
        else:
            glTexImage2D(GL_TEXTURE_2D, 0, internal_format, width, height, 0, format, type, data)
            if use_mipmaps:
                glGenerateMipmap(GL_TEXTURE_2D)
            if setup_parameters:
                if use_mipmaps:
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
                else:
                    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        self.unbind()

    def bind(self):
        if self._samples > 0:
            glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, self._texture)
        else:
            glBindTexture(GL_TEXTURE_2D, self._texture)

    def unbind(self):
        if self._samples > 0:
            glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, 0)
        else:
            glBindTexture(GL_TEXTURE_2D, 0)

    def release(self):
        glDeleteTextures(1, [self._texture])

    def __repr__(self):
        return f"{self.__class__.__name__}(texture={self._texture})"
