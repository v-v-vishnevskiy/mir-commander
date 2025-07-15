import logging

import numpy as np
from OpenGL.GL import (
    GL_FLOAT,
    GL_ARRAY_BUFFER,
    GL_STATIC_DRAW,
    glBindBuffer,
    glBufferData,
    glDeleteBuffers,
    glGenBuffers,
    glEnableVertexAttribArray,
    glVertexAttribPointer,
    glBindVertexArray,
    glGenVertexArrays,
    glDeleteVertexArrays,
)

from .base import Resource

logger = logging.getLogger("ResourceManager.VertexArrayObject")


class VertexArrayObject(Resource):
    __slots__ = ("_vao", "_vbo_vertices", "_vbo_normals")

    def __init__(self, name: str, vertices: np.ndarray, normals: np.ndarray):
        super().__init__(name)

        self._vao = None
        self._vbo_vertices = None
        self._vbo_normals = None

        self._setup_buffers(vertices, normals)

    def bind(self):
        glBindVertexArray(self._vao)

    def unbind(self):
        glBindVertexArray(0)

    def _setup_buffers(self, vertices: np.ndarray, normals: np.ndarray):
        logger.debug("Setting up buffers")
        self._vao = glGenVertexArrays(1)
        self.bind()

        # Generate VBOs
        self._vbo_vertices = glGenBuffers(1)
        self._vbo_normals = glGenBuffers(1)

        # Setup position data
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, False, 0, None)
        glEnableVertexAttribArray(0)  # position

        # Setup normal data
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, False, 0, None)
        glEnableVertexAttribArray(1)  # normal

        self.unbind()

    def __del__(self):
        logger.debug("Cleaning up OpenGL resources")
        if self._vao is not None:
            glDeleteVertexArrays(1, [self._vao])
        if self._vbo_vertices is not None:
            glDeleteBuffers(1, [self._vbo_vertices])
        if self._vbo_normals is not None:
            glDeleteBuffers(1, [self._vbo_normals])

    def __repr__(self):
        return f"VertexArrayObject(name={self.name}, vao={self._vao}, vbo_vertices={self._vbo_vertices}, vbo_normals={self._vbo_normals})"
