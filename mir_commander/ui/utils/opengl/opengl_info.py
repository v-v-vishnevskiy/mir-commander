import logging

import OpenGL.GL as gl
from PySide6.QtGui import QOpenGLContext, QSurfaceFormat

logger = logging.getLogger("OpenGL.Info")


class OpenGLInfo:
    def __init__(self):
        self.context = QOpenGLContext()
        fmt = QSurfaceFormat()
        fmt.setVersion(4, 6)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        self.context.setFormat(fmt)
        self.context.create()

        self.format = self.context.format()
        self.version = (self.format.majorVersion(), self.format.minorVersion())
        self.profile = self.format.profile()
        self.renderable_type = self.format.renderableType()
        self.samples = self.format.samples()
        self.options = self.format.options()

        self.gl_version_string = gl.glGetString(gl.GL_VERSION)
        self.gl_vendor = gl.glGetString(gl.GL_VENDOR)
        self.gl_renderer = gl.glGetString(gl.GL_RENDERER)
        self.gl_extensions = gl.glGetString(gl.GL_EXTENSIONS)

    def as_dict(self):
        return {
            "qt_format_version": self.version,
            "qt_profile": self.profile,
            "qt_renderable_type": self.renderable_type,
            "qt_samples": self.samples,
            "qt_options": self.options,
            "gl_version_string": self.gl_version_string,
            "gl_vendor": self.gl_vendor,
            "gl_renderer": self.gl_renderer,
            "gl_extensions": self.gl_extensions,
        }

    def __str__(self):
        info = self.as_dict()
        return "\n".join(f"{k}: {v}" for k, v in info.items())
