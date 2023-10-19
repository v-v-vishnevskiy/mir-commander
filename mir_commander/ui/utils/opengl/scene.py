import logging
from enum import Enum

from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_MODELVIEW,
    GL_MULTISAMPLE,
    GL_PROJECTION,
    glClear,
    glClearColor,
    glEnable,
    glLoadMatrixf,
    glMatrixMode,
    glViewport,
)
from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, QMatrix4x4, QQuaternion, QVector3D
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from mir_commander.ui.utils.opengl.graphics_items.item import Item
from mir_commander.ui.utils.opengl.utils import Color4f

logger = logging.getLogger(__name__)


class ProjectionMode(Enum):
    Orthographic = 1
    Perspective = 2


class Scene:
    def __init__(self, widget: QOpenGLWidget):
        self.__gl_widget = widget
        self._items: set[Item] = set()
        self._bg_color = (0.0, 0.0, 0.0, 1.0)
        self._translation_matrix = QMatrix4x4()
        self._projection_matrix = QMatrix4x4()
        self._projection_mode = ProjectionMode.Orthographic
        self._fov = 45.0
        self._near_plane = 0.001
        self._far_plane = 10000.0
        self._camera_distance = 10.0
        self._center = QVector3D()
        self._rotation_speed = 1.0
        self._scale_speed = 1.0
        self._rotation = QQuaternion()

    def initialize_gl(self):
        self._setup_projection_matrix()
        self._setup_translation_matrix()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)

    def _setup_projection_matrix(self):
        width = self.__gl_widget.size().width()
        height = self.__gl_widget.size().height()
        glViewport(0, 0, width, height)
        self._projection_matrix.setToIdentity()
        if self._projection_mode == ProjectionMode.Orthographic:
            cd = self._camera_distance * 1.3
            if width <= height:
                self._projection_matrix.ortho(-cd, cd, -cd * (height / width), cd * (height / width), -cd * 10, cd * 10)
            else:
                self._projection_matrix.ortho(-cd * (width / height), cd * (width / height), -cd, cd, -cd * 10, cd * 10)
        elif self._projection_mode == ProjectionMode.Perspective:
            self._projection_matrix.perspective(self._fov, width / height, self._near_plane, self._far_plane)
        else:
            raise RuntimeError("Invalid projection mode")

        self.__gl_widget.makeCurrent()
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self._projection_matrix.data())
        glMatrixMode(GL_MODELVIEW)

    def _setup_translation_matrix(self):
        matrix = self._translation_matrix
        matrix.setToIdentity()
        matrix.translate(0.0, 0.0, -self._camera_distance * 3.6)
        matrix.rotate(self._rotation)
        matrix.translate(-self._center)

    def clear(self):
        for item in self._items:
            item.clear()
        self._items.clear()
        self.__gl_widget.update()

    def add_item(self, item: Item):
        if not issubclass(type(item), Item):
            logger.error(f"Invalid item type: {item.__class__.__name__}")
            return

        self._items.add(item)

    def update_window_size(self):
        self._setup_projection_matrix()
        self.__gl_widget.update()

    def set_projection_mode(self, mode: ProjectionMode | str):
        if type(mode) is str:
            if mode == "perspective":
                mode = ProjectionMode.Perspective
            elif mode == "orthographic":
                mode = ProjectionMode.Orthographic
            else:
                raise RuntimeError(f"Invalid projection mode: {mode}")
        self._projection_mode = mode  # type: ignore
        self._setup_projection_matrix()
        self.__gl_widget.update()

    def toggle_projection_mode(self):
        if self._projection_mode == ProjectionMode.Orthographic:
            self.set_projection_mode(ProjectionMode.Perspective)
        else:
            self.set_projection_mode(ProjectionMode.Orthographic)

    def set_fov(self, value: float):
        self._fov = min(90.0, max(35.0, value))
        self._setup_projection_matrix()
        self.__gl_widget.update()

    def set_far_plane(self, value: float):
        self._far_plane = max(500.0, value)
        self._setup_projection_matrix()
        self.__gl_widget.update()

    def set_center(self, point: QVector3D):
        self._center = point
        self._setup_translation_matrix()
        self.__gl_widget.update()

    def set_camera_distance(self, distance: float):
        self._camera_distance = distance
        self._setup_translation_matrix()
        self._setup_projection_matrix()
        self.__gl_widget.update()

    def set_current(self):
        self._setup_projection_matrix()
        self.__gl_widget.update()

    def set_background_color(self, color: Color4f):
        self._bg_color = color
        self.__gl_widget.update()

    @property
    def translation_matrix(self) -> QMatrix4x4:
        return self._translation_matrix

    @property
    def projection_matrix(self) -> QMatrix4x4:
        return self._projection_matrix

    def rotate(self, pitch: float, yaw: float, roll: float = 0.0):
        speed = self._rotation_speed
        r = QQuaternion.fromEulerAngles(pitch * speed, -yaw * speed, roll * speed)
        r *= self._rotation
        self._rotation = r
        self._setup_translation_matrix()
        self.__gl_widget.update()

    def scale(self, factor: float):
        self.set_camera_distance(self._camera_distance + (factor * self._scale_speed) * self._camera_distance)

    def move_cursor(self, x: int, y: int):
        pass

    def paint(self):
        glLoadMatrixf(self._translation_matrix.data())
        glClearColor(*self._bg_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        for item in self._items:
            item.paint()

    def point_to_line(self, x: int, y: int) -> tuple[QVector3D, QVector3D]:
        width = self.__gl_widget.size().width()
        height = self.__gl_widget.size().height()
        viewport = QRect(0, 0, width, height)

        y = height - y  # opengl computes from left-bottom corner
        return (
            QVector3D(x, y, -1.0).unproject(self._translation_matrix, self._projection_matrix, viewport),
            QVector3D(x, y, 1.0).unproject(self._translation_matrix, self._projection_matrix, viewport),
        )

    def update(self):
        self.__gl_widget.update()

    def render_to_image(self, width: int, height: int, transparent_bg: bool = False) -> QImage:
        self.__gl_widget.makeCurrent()

        fbo_format = QOpenGLFramebufferObjectFormat()
        fbo_format.setSamples(16)
        fbo_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        fbo = QOpenGLFramebufferObject(width, height, fbo_format)
        fbo.bind()

        bg_color = self._bg_color

        if transparent_bg:
            self._bg_color = bg_color[0], bg_color[1], bg_color[2], 0.0

        w = self.__gl_widget.size().width()
        h = self.__gl_widget.size().height()

        glViewport(0, 0, width, height)
        self.paint()
        glViewport(0, 0, w, h)
        self._bg_color = bg_color

        fbo.release()

        image = fbo.toImage()

        if not transparent_bg:
            image = image.convertToFormat(QImage.Format_RGB32)

        return image
