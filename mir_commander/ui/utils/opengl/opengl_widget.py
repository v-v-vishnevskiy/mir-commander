import logging
from OpenGL.GL import GL_DEPTH_TEST, GL_MULTISAMPLE, glEnable
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QMouseEvent, QSurfaceFormat, QVector3D, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from .action_handler import ActionHandler
from .camera import Camera
from .enums import ClickAndMoveMode, ProjectionMode, WheelMode
from .keymap import Keymap
from .renderer import Renderer
from .scene import Scene
from .utils import Color4f

logger = logging.getLogger("OpenGL.Widget")


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget, keymap: None | Keymap = None, antialiasing: bool = True):
        super().__init__(parent)

        self._cursor_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale
        self._rotation_speed = 1.0
        self._scale_speed = 1.0

        # Initialize components
        self.action_handler = ActionHandler(keymap)
        self.camera = Camera()
        self.scene = Scene()
        self.renderer = Renderer(self.camera, self.scene)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        if antialiasing:
            sf = QSurfaceFormat()
            sf.setSamples(16)
            self.setFormat(sf)

        self._init_actions()

    def clear(self, update: bool = True):
        self.scene.clear()
        if update:
            self.update()

    def _init_actions(self):
        self.action_handler.add_action("rotate_down", True, self.rotate_scene, 1, 0)
        self.action_handler.add_action("rotate_left", True, self.rotate_scene, 0, -1)
        self.action_handler.add_action("rotate_right", True, self.rotate_scene, 0, 1)
        self.action_handler.add_action("rotate_up", True, self.rotate_scene, -1, 0)
        self.action_handler.add_action("zoom_in", True, self.scale_scene, 1.015)
        self.action_handler.add_action("zoom_out", True, self.scale_scene, 0.975)

    @property
    def cursor_position(self) -> tuple[int, int]:
        return self._cursor_pos.x(), self._cursor_pos.y()

    def initializeGL(self):
        self.makeCurrent()
        self.camera.setup_projection_matrix(self.size().width(), self.size().height())
        self.camera.setup_translation_matrix()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)

    def resize(self, w: int, h: int):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.resize(w, h)
        else:
            super().resize(w, h)

    def resizeGL(self, w: int, h: int):
        self.makeCurrent()
        self.camera.setup_projection_matrix(w, h)
        self.update()

    def paintGL(self):
        self.renderer.paint()

    def setWindowIcon(self, icon: QIcon):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.setWindowIcon(icon)
        else:
            super().setWindowIcon(icon)

    def keyPressEvent(self, event: QKeyEvent):
        self.action_handler.call_action(event, self.action_handler.keymap.match_key_event)

    def keyReleaseEvent(self, event: QKeyEvent):
        self.action_handler.stop_action(event, self.action_handler.keymap.match_key_event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._click_and_move_mode == ClickAndMoveMode.Rotation:
                diff = pos - self._cursor_pos
                self.rotate_scene(diff.y(), diff.x())
        else:
            self.new_cursor_position(pos.x(), pos.y())

        self._cursor_pos = pos

    def mousePressEvent(self, event: QMouseEvent):
        self.action_handler.call_action(event, self.action_handler.keymap.match_mouse_event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.action_handler.stop_action(event, self.action_handler.keymap.match_mouse_event)

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
            self.action_handler.call_action(event, self.action_handler.keymap.match_wheel_event)

    def set_camera_projection_mode(self, mode: ProjectionMode | str):
        self.makeCurrent()
        self.camera.set_projection_mode(mode)
        self.camera.setup_projection_matrix(self.size().width(), self.size().height())
        self.update()

    def toggle_camera_projection_mode(self):
        self.makeCurrent()
        self.camera.toggle_projection_mode()
        self.camera.setup_projection_matrix(self.size().width(), self.size().height())
        self.update()

    def set_camera_fov(self, value: float):
        self.makeCurrent()
        self.camera.set_fov(value)
        self.camera.setup_projection_matrix(self.size().width(), self.size().height())
        self.update()

    def set_camera_position(self, point: QVector3D):
        self.camera.set_position(point)
        self.update()

    def set_camera_distance(self, distance: float):
        self.makeCurrent()
        self.camera.set_camera_distance(distance)
        self.camera.setup_projection_matrix(self.size().width(), self.size().height())
        self.update()

    def set_background_color(self, color: Color4f):
        self.renderer.set_background_color(color)
        self.update()

    def rotate_scene(self, pitch: float, yaw: float, roll: float = 0.0):
        self.scene.rotate(pitch, yaw, roll)
        self.update()

    def scale_scene(self, factor: float):
        self.scene.scale(factor)
        self.update()

    def translate_scene(self, x: float, y: float, z: float):
        self.scene.translate(x, y, z)
        self.update()

    def reset_scene_transform(self):
        self.scene.reset_transform()
        self.update()

    def new_cursor_position(self, x: int, y: int):
        pass

    def point_to_line(self, x: int, y: int):
        return self.renderer.point_to_line(x, y, self.size().width(), self.size().height())

    def render_to_image(
        self, width: int, height: int, transparent_bg: bool = False, crop_to_content: bool = False
    ):
        return self.renderer.render_to_image(
            width, height, transparent_bg, crop_to_content, self.makeCurrent
        )
