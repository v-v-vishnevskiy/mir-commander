from OpenGL.GL import GL_FRAGMENT_SHADER, GL_VERTEX_SHADER, GLuint, glDeleteShader
from OpenGL.GL.shaders import compileProgram, compileShader


class Shader:
    def __init__(self, shader_type, code: str):
        self.__shader_type = shader_type
        self.__code = code
        self.__shader: GLuint = None

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
        self.__program: GLuint = None

    @property
    def program(self) -> GLuint:
        if self.__program is None:
            self.__program = compileProgram(*[s.shader for s in self._shaders])
        return self.__program

    def __del__(self):
        pass
