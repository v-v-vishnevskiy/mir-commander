from mir_commander.core.errors import CoreError


class OpenGLError(CoreError):
    pass


class FramebufferError(OpenGLError):
    pass


class RendererError(OpenGLError):
    pass
