import logging

import numpy as np
from OpenGL.GL import (
    GL_ARRAY_BUFFER,
    GL_FLOAT,
    GL_STATIC_DRAW,
    glBindBuffer,
    glBindVertexArray,
    glBufferData,
    glDeleteBuffers,
    glDeleteVertexArrays,
    glEnableVertexAttribArray,
    glGenBuffers,
    glGenVertexArrays,
    glVertexAttribPointer,
)

from .base import Resource

logger = logging.getLogger("OpenGL.VertexArrayObject")


class VertexArrayObject(Resource):
    __slots__ = ("_vao", "_vbo_vertices", "_vbo_normals", "_vbo_tex_coords", "_triangles_count")

    def __init__(self, name: str, vertices: np.ndarray, normals: np.ndarray, tex_coords: None | np.ndarray = None):
        super().__init__(name)

        self._vao = glGenVertexArrays(1)
        self._vbo_vertices = glGenBuffers(1)
        self._vbo_normals = glGenBuffers(1)
        self._vbo_tex_coords = glGenBuffers(1)
        self._triangles_count = int(len(vertices) / 3)
        self._setup_buffers(
            vertices, normals, tex_coords if tex_coords is not None else np.array([0] * len(vertices), dtype=np.float32)
        )

    @property
    def triangles_count(self) -> int:
        return self._triangles_count

    def bind(self):
        glBindVertexArray(self._vao)

    def unbind(self):
        glBindVertexArray(0)

    def _setup_buffers(self, vertices: np.ndarray, normals: np.ndarray, tex_coords: np.ndarray):
        logger.debug("Setup buffers: %s", self.name)

        self.bind()

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

        # Setup tex_coords data
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_tex_coords)
        glBufferData(GL_ARRAY_BUFFER, tex_coords.nbytes, tex_coords, GL_STATIC_DRAW)
        glVertexAttribPointer(2, 2, GL_FLOAT, False, 0, None)
        glEnableVertexAttribArray(2)  # tex_coords

        glBindVertexArray(0)

    def release(self):
        logger.debug("Deleting resources: %s", self.name)

        glDeleteVertexArrays(1, [self._vao])
        glDeleteBuffers(1, [self._vbo_vertices])
        glDeleteBuffers(1, [self._vbo_normals])
        glDeleteBuffers(1, [self._vbo_tex_coords])

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, vao={self._vao}, vbo_vertices={self._vbo_vertices}, vbo_normals={self._vbo_normals}, vbo_tex_coords={self._vbo_tex_coords})"
