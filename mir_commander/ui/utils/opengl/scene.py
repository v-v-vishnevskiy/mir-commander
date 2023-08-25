import logging
from enum import Enum

from OpenGL.GL import (
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_MODELVIEW,
    GL_PROJECTION,
    glClear,
    glClearColor,
    glLoadMatrixf,
    glMatrixMode,
    glViewport,
)
from PySide6.QtCore import QRect
from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from mir_commander.ui.utils.opengl.graphics_items.item import Item

logger = logging.getLogger(__name__)


class ProjectionMode(Enum):
    Orthographic = 1
    Perspective = 2


class Scene:
    def __init__(self, parent: QOpenGLWidget):
        self.__parent = parent
        self._items: set[Item] = set()
        self._bg_color = (0.0, 0.0, 0.0, 1.0)
        self._translation_matrix = QMatrix4x4()
        self._projection_matrix = QMatrix4x4()
        self._projection_mode = ProjectionMode.Perspective
        self._perspective_projection_settings = {"fov": 45.0, "near_plane": 0.001, "far_plane": 50.0}
        self._camera_distance = 10.0
        self._scale_factor = 1.0
        self._rotation_speed = 1.0
        self._scale_speed = 1.0
        self._rotation = QQuaternion()

        self._setup_projection_matrix()
        self._setup_translation_matrix()

    def _setup_projection_matrix(self):
        width = self.__parent.size().width()
        height = self.__parent.size().height()
        glViewport(0, 0, width, height)
        self._projection_matrix.setToIdentity()
        if self._projection_mode == ProjectionMode.Orthographic:
            cd = self._camera_distance
            if width <= height:
                self._projection_matrix.ortho(-cd, cd, -cd * (height / width), cd * (height / width), -cd, cd)
            else:
                self._projection_matrix.ortho(-cd * (width / height), cd * (width / height), -cd, cd, -cd, cd)
        elif self._projection_mode == ProjectionMode.Perspective:
            fov = self._perspective_projection_settings["fov"]
            near_plane = self._perspective_projection_settings["near_plane"]
            far_plane = self._perspective_projection_settings["far_plane"]
            self._projection_matrix.perspective(fov, width / height, near_plane, far_plane)
        else:
            raise RuntimeError("Invalid projection mode")

        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self._projection_matrix.data())
        glMatrixMode(GL_MODELVIEW)

    def _setup_translation_matrix(self):
        matrix = self._translation_matrix
        matrix.setToIdentity()
        matrix.translate(0, 0, -self._camera_distance)
        matrix.scale(self._scale_factor)
        matrix.rotate(self._rotation)

    def add_item(self, item: Item):
        if not issubclass(type(item), Item):
            logger.error(f"Invalid item type: {item.__class__.__name__}")
            return

        self._items.add(item)

    def update_window_size(self):
        self._setup_projection_matrix()
        self.__parent.update()

    def set_projection_mode(self, mode: ProjectionMode):
        self._projection_mode = mode
        self._setup_projection_matrix()
        self.__parent.update()

    def set_fov(self, value: float):
        self._perspective_projection_settings["fov"] = max(35.0, value)
        self._setup_projection_matrix()
        self.__parent.update()

    def set_far_plane(self, value: float):
        self._perspective_projection_settings["far_plane"] = max(1.0, value)
        self._setup_projection_matrix()
        self.__parent.update()

    def set_current(self):
        self._setup_projection_matrix()
        self.__parent.update()

    def set_background_color(self, red: float, green: float, blue: float, alpha: float = 1.0):
        self._bg_color = (red, green, blue, alpha)
        glClearColor(*self._bg_color)
        self.__parent.update()

    @property
    def translation_matrix(self) -> QMatrix4x4:
        return self._translation_matrix

    @property
    def projection_matrix(self) -> QMatrix4x4:
        return self._projection_matrix

    def set_translation_matrix(self, matrix: QMatrix4x4):
        self._translation_matrix = matrix
        self.__parent.update()

    def set_projection_matrix(self, matrix: QMatrix4x4):
        self._projection_matrix = matrix
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self._projection_matrix.data())
        glMatrixMode(GL_MODELVIEW)
        self.__parent.update()

    def rotate(self, pitch: float, yaw: float, roll: float = 0.0):
        speed = self._rotation_speed
        r = QQuaternion.fromEulerAngles(pitch * speed, -yaw * speed, roll * speed)
        r *= self._rotation
        self._rotation = r
        self._setup_translation_matrix()
        self.__parent.update()

    def scale(self, factor: float):
        self._scale_factor *= factor * self._scale_speed
        self._setup_translation_matrix()
        self.__parent.update()

    def paint(self):
        glLoadMatrixf(self._translation_matrix.data())
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        for item in self._items:
            item.paint()

    def point_to_line(self, x: int, y: int) -> tuple[QVector3D, QVector3D]:
        width = self.__parent.size().width()
        height = self.__parent.size().height()
        viewport = QRect(0, 0, width, height)

        y = height - y  # opengl computes from left-bottom corner
        return (
            QVector3D(x, y, -1.0).unproject(self._translation_matrix, self._projection_matrix, viewport),
            QVector3D(x, y, 1.0).unproject(self._translation_matrix, self._projection_matrix, viewport),
        )
