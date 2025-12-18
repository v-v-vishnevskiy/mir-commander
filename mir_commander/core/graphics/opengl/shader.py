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

from .errors import OpenGLError


class UniformLocations:
    __slots__ = (
        "scene_matrix",
        "view_matrix",
        "projection_matrix",
        "transform_matrix",
        "is_transparent",
        "is_picking",
        "is_orthographic",
    )

    def __init__(self):
        self.scene_matrix: GLuint | None = None
        self.view_matrix: GLuint | None = None
        self.projection_matrix: GLuint | None = None
        self.transform_matrix: GLuint | None = None
        self.is_transparent: GLuint | None = None
        self.is_picking: GLuint | None = None
        self.is_orthographic: GLuint | None = None


class _Shader:
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


class VertexShader(_Shader):
    def __init__(self, code: str):
        super().__init__(GL_VERTEX_SHADER, code)


class FragmentShader(_Shader):
    def __init__(self, code: str):
        super().__init__(GL_FRAGMENT_SHADER, code)


class ShaderProgram:
    __slots__ = ("_shaders", "_program", "uniform_locations")

    def __init__(self, *shaders: VertexShader | FragmentShader):
        try:
            self._program = compileProgram(*[s.shader for s in shaders], validate=False)
        except ShaderCompilationError as e:
            raise OpenGLError(f"Failed to compile shader program: {e}")
        except ShaderValidationError as e:
            raise OpenGLError(f"Failed to validate shader program: {e}")
        except ShaderLinkError as e:
            raise OpenGLError(f"Failed to link shader program: {e}")

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
        self.uniform_locations.transform_matrix = glGetUniformLocation(self._program, "transform_matrix")
        self.uniform_locations.is_transparent = glGetUniformLocation(self._program, "is_transparent")
        self.uniform_locations.is_picking = glGetUniformLocation(self._program, "is_picking")
        self.uniform_locations.is_orthographic = glGetUniformLocation(self._program, "is_orthographic")

        glUseProgram(0)

    def release(self):
        glDeleteProgram(self._program)

    def __repr__(self):
        return f"{self.__class__.__name__}(program={self._program})"
