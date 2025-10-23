import logging

from OpenGL.GL import (
    GL_FRAGMENT_SHADER,
    GL_VERTEX_SHADER,
    GLuint,
    glDeleteProgram,
    glGetUniformLocation,
    glUseProgram,
)
from OpenGL.GL.shaders import (
    ShaderCompilationError,
    ShaderLinkError,
    ShaderValidationError,
    compileProgram,
    compileShader,
)

from .base import Resource

logger = logging.getLogger("OpenGL.Shader")


class UniformLocations:
    __slots__ = ("scene_matrix", "view_matrix", "projection_matrix")

    def __init__(self):
        self.scene_matrix: GLuint | None = None
        self.view_matrix: GLuint | None = None
        self.projection_matrix: GLuint | None = None


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
        return f"{self.__class__.__name__}(type={self._shader_type}, shader={self._shader})"


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

        try:
            self._program = compileProgram(*[s.shader for s in shaders], validate=False)
        except ShaderCompilationError as e:
            logger.error("Failed to compile shader program `%s`: %s", name, e)
            raise e
        except ShaderValidationError as e:
            logger.error("Failed to validate shader program `%s`: %s", name, e)
            raise e
        except ShaderLinkError as e:
            logger.error("Failed to link shader program `%s`: %s", name, e)
            raise e

        self.uniform_locations = UniformLocations()
        self._cache_uniform_locations()

    @property
    def program(self) -> GLuint:
        return self._program

    def use(self):
        glUseProgram(self._program)

    def _cache_uniform_locations(self):
        self.use()

        self.uniform_locations.scene_matrix = glGetUniformLocation(self._program, "scene_matrix")
        self.uniform_locations.view_matrix = glGetUniformLocation(self._program, "view_matrix")
        self.uniform_locations.projection_matrix = glGetUniformLocation(self._program, "projection_matrix")

        glUseProgram(0)

    def release(self):
        logger.debug("Deleting resources: %s", self.name)

        glDeleteProgram(self._program)

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name})"
