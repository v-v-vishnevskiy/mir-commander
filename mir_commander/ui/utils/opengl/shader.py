from OpenGL.GL import GL_FRAGMENT_SHADER, GL_VERTEX_SHADER, GLuint, glDeleteShader, glGetUniformLocation, glUseProgram
from OpenGL.GL.shaders import compileProgram, compileShader


class UniformLocations:
    __slots__ = ("model_matrix", "scene_matrix", "view_matrix", "projection_matrix", "color")

    def __init__(self):
        self.model_matrix: GLuint | None = None
        self.scene_matrix: GLuint | None = None
        self.view_matrix: GLuint | None = None
        self.projection_matrix: GLuint | None = None
        self.color: GLuint | None = None

class Shader:
    def __init__(self, shader_type, code: str):
        self.__shader_type = shader_type
        self.__code = code
        self.__shader: GLuint | None = None

    @property
    def shader(self) -> GLuint:
        if self.__shader is None:
            self.__shader = compileShader(self.__code, self.__shader_type)
        return self.__shader

    def __del__(self):
        if self.__shader is not None:
            glDeleteShader(self.__shader)
        self.__shader = None


class VertexShader(Shader):
    def __init__(self, code: str):
        super().__init__(GL_VERTEX_SHADER, code)


class FragmentShader(Shader):
    def __init__(self, code: str):
        super().__init__(GL_FRAGMENT_SHADER, code)


class ShaderProgram:
    def __init__(self, *shaders: VertexShader | FragmentShader):
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
        pass
