from OpenGL.GL import (
    GL_FRAGMENT_SHADER,
    GL_VERTEX_SHADER,
    GLuint,
    glDeleteProgram,
    glGetUniformLocation,
    glUseProgram,
)
from OpenGL.GL.shaders import compileProgram, compileShader

from .base import Resource


class UniformLocations:
    __slots__ = ("model_matrix", "scene_matrix", "view_matrix", "projection_matrix", "color")

    def __init__(self):
        self.model_matrix: GLuint | None = None
        self.scene_matrix: GLuint | None = None
        self.view_matrix: GLuint | None = None
        self.projection_matrix: GLuint | None = None
        self.color: GLuint | None = None


class Shader:
    __slots__ = ("_shader_type", "_code", "_shader")

    def __init__(self, shader_type, code: str):
        self._shader_type = shader_type
        self._code = code
        self._shader: GLuint | None = None

    @property
    def shader(self) -> GLuint:
        if self._shader is None:
            self._shader = compileShader(self._code, self._shader_type)
        return self._shader

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, type={self._shader_type}, shader={self._shader})"


class VertexShader(Shader):
    def __init__(self, code: str):
        super().__init__(GL_VERTEX_SHADER, code)


class FragmentShader(Shader):
    def __init__(self, code: str):
        super().__init__(GL_FRAGMENT_SHADER, code)


class ShaderProgram(Resource):
    __slots__ = ("_shaders", "_program", "uniform_locations")

    def __init__(self, name: str, *shaders: VertexShader | FragmentShader):
        super().__init__(name)

        self._shaders = shaders
        self._program: GLuint | None = None
        self.uniform_locations = UniformLocations()

    @property
    def program(self) -> GLuint:
        if self._program is None:
            self._program = compileProgram(*[s.shader for s in self._shaders], validate=False)
            self._cache_uniform_locations()
        return self._program

    def _cache_uniform_locations(self):
        program = self.program
        glUseProgram(program)

        self.uniform_locations.model_matrix = glGetUniformLocation(program, "model_matrix")
        self.uniform_locations.scene_matrix = glGetUniformLocation(program, "scene_matrix")
        self.uniform_locations.view_matrix = glGetUniformLocation(program, "view_matrix")
        self.uniform_locations.projection_matrix = glGetUniformLocation(program, "projection_matrix")
        self.uniform_locations.color = glGetUniformLocation(program, "color")

        glUseProgram(0)

    def __del__(self):
        if self._program is not None:
            glDeleteProgram(self._program)
            self._program = None

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
