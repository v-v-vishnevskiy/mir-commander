import logging
from enum import Enum
from typing import Callable

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
from PySide6.QtCore import QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QImage, QKeyEvent, QMatrix4x4, QMouseEvent, QQuaternion, QSurfaceFormat, QVector3D, QWheelEvent
from PySide6.QtOpenGL import QOpenGLFramebufferObject, QOpenGLFramebufferObjectFormat
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from .keymap import Keymap
from .graphics_items.item import Item
from .utils import Color4f

logger = logging.getLogger("OpenGL.Widget")


class ClickAndMoveMode(Enum):
    Nothing = 0
    Rotation = 1


class WheelMode(Enum):
    Nothing = 0
    Scale = 1


class ProjectionMode(Enum):
    Orthographic = 1
    Perspective = 2


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget, keymap: None | Keymap = None, antialiasing: bool = True):
        super().__init__(parent)

        self._cursor_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale

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

        self._keymap = keymap or Keymap(
            id(self),
            {
                "rotate_down": ["down"],
                "rotate_left": ["left"],
                "rotate_right": ["right"],
                "rotate_up": ["up"],
                "zoom_in": ["wheel_up", "="],
                "zoom_out": ["wheel_down", "-"],
            },
        )
        self._actions: dict[str, tuple[bool, Callable, tuple]] = {}
        self._init_actions()

        self.setMouseTracking(True)

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self._to_repeat_actions: dict[str, tuple[Callable, tuple]] = {}
        self._repeatable_actions_timer = QTimer()
        self._repeatable_actions_timer.timeout.connect(self._call_action_timer)
        if antialiasing:
            sf = QSurfaceFormat()
            sf.setSamples(16)
            self.setFormat(sf)

    def _init_actions(self):
        # TODO: document why do we need such a complicated system for managing of actions
        self._actions["rotate_down"] = (True, self.rotate, (1, 0))
        self._actions["rotate_left"] = (True, self.rotate, (0, 1))
        self._actions["rotate_right"] = (True, self.rotate, (0, -1))
        self._actions["rotate_up"] = (True, self.rotate, (-1, 0))
        self._actions["zoom_in"] = (True, self.scale, (-0.015,))
        self._actions["zoom_out"] = (True, self.scale, (0.015,))
    
    def _call_action(self, event: QKeyEvent | QMouseEvent | str, match_fn: Callable):
        action = match_fn(event)
        try:
            repeatable, fn, args = self._actions[action]
            if repeatable and type(event) in (QKeyEvent, QMouseEvent):
                self._to_repeat_actions[action] = fn, args
                self._repeatable_actions_timer.start()
            else:
                fn(*args)
        except KeyError:
            pass

    def _stop_action(self, event: QKeyEvent | QMouseEvent, match_fn: Callable):
        action = match_fn(event)
        try:
            repeatable, fn, args = self._actions[action]
            if repeatable and type(event) in (QKeyEvent, QMouseEvent):
                del self._to_repeat_actions[action]
        except KeyError:
            pass

    def _call_action_timer(self):
        if not self._to_repeat_actions:
            self._repeatable_actions_timer.stop()
        else:
            for fn, args in self._to_repeat_actions.values():
                fn(*args)

    def _setup_projection_matrix(self):
        width = self.size().width()
        height = self.size().height()
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

        self.makeCurrent()
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self._projection_matrix.data())
        glMatrixMode(GL_MODELVIEW)

    def _setup_translation_matrix(self):
        matrix = self._translation_matrix
        matrix.setToIdentity()
        matrix.translate(0.0, 0.0, -self._camera_distance * 3.6)
        matrix.rotate(self._rotation)
        matrix.translate(-self._center)

    def clear(self, update: bool = True):
        for item in self._items:
            item.clear()
        self._items.clear()
        if update:
            self.update()

    def add_item(self, item: Item):
        if not issubclass(type(item), Item):
            logger.error(f"Invalid item type: {item.__class__.__name__}")
            return

        self._items.add(item)

    def remove_item(self, item: Item):
        self._items.remove(item)

    @property
    def cursor_position(self) -> tuple[int, int]:
        return self._cursor_pos.x(), self._cursor_pos.y()

    def initializeGL(self):
        self._setup_projection_matrix()
        self._setup_translation_matrix()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)

    def resize(self, w: int, h: int):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.resize(w, h)
        else:
            super().resize(w, h)

    def resizeGL(self, w: int, h: int):
        self._setup_projection_matrix()
        self.update()

    def paintGL(self):
        glLoadMatrixf(self._translation_matrix.data())
        glClearColor(*self._bg_color)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        for item in self._items:
            item.paint()

    def setWindowIcon(self, icon: QIcon):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.setWindowIcon(icon)
        else:
            super().setWindowIcon(icon)

    def keyPressEvent(self, event: QKeyEvent):
        self._call_action(event, self._keymap.match_key_event)

    def keyReleaseEvent(self, event: QKeyEvent):
        self._stop_action(event, self._keymap.match_key_event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._click_and_move_mode == ClickAndMoveMode.Rotation:
                diff = pos - self._cursor_pos
                self.rotate(diff.y(), -diff.x())
        else:
            self.new_cursor_position(pos.x(), pos.y())

        self._cursor_pos = pos

    def mousePressEvent(self, event: QMouseEvent):
        self._call_action(event, self._keymap.match_mouse_event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._stop_action(event, self._keymap.match_mouse_event)

    def wheelEvent(self, event: QWheelEvent):
        events: list[str] = []
        delta = event.angleDelta().x()
        if delta > 0:
            events.append("wheel_left")
        elif delta < 0:
            events.append("wheel_right")

        delta = event.angleDelta().y()
        if delta > 0:
            events.append("wheel_up")
        elif delta < 0:
            events.append("wheel_down")

        for event in events:
            self._call_action(event, self._keymap.match_wheel_event)

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
        self.update()

    def toggle_projection_mode(self):
        if self._projection_mode == ProjectionMode.Orthographic:
            self.set_projection_mode(ProjectionMode.Perspective)
        else:
            self.set_projection_mode(ProjectionMode.Orthographic)

    def set_fov(self, value: float):
        self._fov = min(90.0, max(35.0, value))
        self._setup_projection_matrix()
        self.update()

    def set_far_plane(self, value: float):
        self._far_plane = max(500.0, value)
        self._setup_projection_matrix()
        self.update()

    def set_center(self, point: QVector3D):
        self._center = point
        self._setup_translation_matrix()
        self.update()

    def set_camera_distance(self, distance: float):
        self._camera_distance = distance
        self._setup_translation_matrix()
        self._setup_projection_matrix()
        self.update()

    def set_current(self):
        self._setup_projection_matrix()
        self.update()

    def set_background_color(self, color: Color4f):
        self._bg_color = color
        self.update()

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
        self.update()

    def scale(self, factor: float):
        self.set_camera_distance(self._camera_distance + (factor * self._scale_speed) * self._camera_distance)

    def new_cursor_position(self, x: int, y: int):
        pass

    def point_to_line(self, x: int, y: int) -> tuple[QVector3D, QVector3D]:
        width = self.size().width()
        height = self.size().height()
        viewport = QRect(0, 0, width, height)

        y = height - y  # opengl computes from left-bottom corner
        return (
            QVector3D(x, y, -1.0).unproject(self._translation_matrix, self._projection_matrix, viewport),
            QVector3D(x, y, 1.0).unproject(self._translation_matrix, self._projection_matrix, viewport),
        )

    def crop_image_to_content(self, image: QImage, bg_color: QColor) -> QImage:
        # Need this hack with the fake 1x1 image to take into account the format of our real image
        # so we know the value of the background color as it is represented in the image.
        bg_image = QImage(1, 1, image.format())
        bg_image.setPixelColor(0, 0, bg_color)
        bg_color_value = bg_image.pixel(0, 0)
        xmin = ymin = xmax = ymax = -1

        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixel(x, y) != bg_color_value:
                    ymin = y
                    break
            if ymin >= 0:
                break

        for y in reversed(range(image.height())):
            for x in range(image.width()):
                if image.pixel(x, y) != bg_color_value:
                    ymax = y
                    break
            if ymax >= 0:
                break

        for x in range(image.width()):
            for y in range(image.height()):
                if image.pixel(x, y) != bg_color_value:
                    xmin = x
                    break
            if xmin >= 0:
                break

        for x in reversed(range(image.width())):
            for y in range(image.height()):
                if image.pixel(x, y) != bg_color_value:
                    xmax = x
                    break
            if xmax >= 0:
                break

        if xmin >= 0 and xmax >= 0 and ymin >= 0 and ymax >= 0:
            crop_area = QRect(xmin, ymin, xmax - xmin + 1, ymax - ymin + 1)
            image = image.copy(crop_area)

        return image

    def render_to_image(
        self, width: int, height: int, transparent_bg: bool = False, crop_to_content: bool = False
    ) -> QImage:
        self.makeCurrent()

        fbo_format = QOpenGLFramebufferObjectFormat()
        fbo_format.setSamples(16)
        fbo_format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
        fbo = QOpenGLFramebufferObject(width, height, fbo_format)
        fbo.bind()

        bg_color_bak = self._bg_color

        if transparent_bg:
            self._bg_color = bg_color_bak[0], bg_color_bak[1], bg_color_bak[2], 0.0

        bg_color = QColor.fromRgbF(*self._bg_color)

        w = self.size().width()
        h = self.size().height()

        glViewport(0, 0, width, height)
        self.paintGL()
        glViewport(0, 0, w, h)
        self._bg_color = bg_color_bak

        fbo.release()

        image = fbo.toImage()

        if not transparent_bg:
            image = image.convertToFormat(QImage.Format_RGB32)

        if crop_to_content:
            image = self.crop_image_to_content(image, bg_color)

        return image
