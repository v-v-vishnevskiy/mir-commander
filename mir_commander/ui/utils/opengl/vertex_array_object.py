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


class VertexArrayObject:
    __slots__ = ("vao",  "count", "_vbo_vertices", "_vbo_normals")

    def __init__(self, vertices: np.ndarray, normals: np.ndarray):
        self.vao = glGenVertexArrays(1)
        self.count = 0
        self._vbo_vertices = None
        self._vbo_normals = None
        self._setup_buffers(vertices, normals)

    def _setup_buffers(self, vertices: np.ndarray, normals: np.ndarray):
        self.count = int(len(vertices) / 3)

        glBindVertexArray(self.vao)

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

        # Unbind VAO
        glBindVertexArray(0)

    def update(self, vertices: np.ndarray, normals: np.ndarray):
        """Update VBO data when mesh data changes"""

        self.count = int(len(vertices) / 3)

        glBindVertexArray(self.vao)

        # Update vertex data
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_vertices)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # Update normal data
        glBindBuffer(GL_ARRAY_BUFFER, self._vbo_normals)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)

        glBindVertexArray(0)

    def __del__(self):
        """Cleanup OpenGL resources"""
        if self.vao is not None:
            glDeleteVertexArrays(1, [self.vao])
        if self._vbo_vertices is not None:
            glDeleteBuffers(1, [self._vbo_vertices])
        if self._vbo_normals is not None:
            glDeleteBuffers(1, [self._vbo_normals])
