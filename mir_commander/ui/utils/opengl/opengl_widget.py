import logging
from OpenGL.GL import GL_MULTISAMPLE, glEnable, glViewport, glMatrixMode, glLoadMatrixf, GL_PROJECTION, GL_MODELVIEW
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QMouseEvent, QVector3D, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from .action_handler import ActionHandler
from .camera import Camera
from .graphics_items.item import Item
from .enums import ClickAndMoveMode, ProjectionMode, WheelMode
from .keymap import Keymap
from .projection import ProjectionManager
from .renderer import Renderer
from .scene import Scene
from .utils import Color4f, color_to_id

logger = logging.getLogger("OpenGL.Widget")


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent: QWidget, keymap: None | Keymap = None, fallback_mode: bool = False):
        super().__init__(parent)

        self._cursor_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale
        self._rotation_speed = 1.0
        self._scale_speed = 1.0
        self._fallback_mode = fallback_mode

        # Initialize components
        self.action_handler = ActionHandler(keymap)
        self.camera = Camera()
        self.projection_manager = ProjectionManager(width=self.size().width(), height=self.size().height())
        self.scene = Scene(self.camera)
        self.renderer = Renderer(self.projection_manager, self.scene, self.camera, fallback_mode)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self._init_actions()

    def init(self):
        pass

    def clear(self):
        self.scene.clear()

    def _init_actions(self):
        self.action_handler.add_action("rotate_up", True, self.rotate_scene, -1, 0)
        self.action_handler.add_action("rotate_down", True, self.rotate_scene, 1, 0)
        self.action_handler.add_action("rotate_left", True, self.rotate_scene, 0, -1)
        self.action_handler.add_action("rotate_right", True, self.rotate_scene, 0, 1)
        self.action_handler.add_action("zoom_in", True, self.scale_scene, 1.015)
        self.action_handler.add_action("zoom_out", True, self.scale_scene, 0.975)

    def _setup_projection(self, w: int, h: int):
        glViewport(0, 0, w, h)
        if self._fallback_mode:
            glMatrixMode(GL_PROJECTION)
            glLoadMatrixf(self.projection_manager.active_projection.matrix.data())
            glMatrixMode(GL_MODELVIEW)

    @property
    def cursor_position(self) -> tuple[int, int]:
        return self._cursor_pos.x(), self._cursor_pos.y()

    def initializeGL(self):
        self.makeCurrent()
        self.projection_manager.build_projections(self.size().width(), self.size().height())
        self._setup_projection(self.size().width(), self.size().height())
        glEnable(GL_MULTISAMPLE)
        self.init()

    def resize(self, w: int, h: int):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.resize(w, h)
        else:
            super().resize(w, h)

    def resizeGL(self, w: int, h: int):
        self.makeCurrent()
        self.projection_manager.build_projections(w, h)
        self._setup_projection(w, h)
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

    def set_projection_mode(self, mode: ProjectionMode | str):
        self.makeCurrent()
        self.projection_manager.set_projection_mode(mode)
        self._setup_projection(self.size().width(), self.size().height())
        self.update()

    def toggle_projection_mode(self):
        self.makeCurrent()
        self.projection_manager.toggle_projection_mode()
        self._setup_projection(self.size().width(), self.size().height())
        self.update()

    def set_perspective_projection_fov(self, value: float):
        self.makeCurrent()
        self.projection_manager.perspective_projection.set_fov(value)
        self.projection_manager.build_projections(self.size().width(), self.size().height())
        self._setup_projection(self.size().width(), self.size().height())
        self.update()

    def set_scene_position(self, point: QVector3D):
        self.scene.set_position(point)
        self.update()

    def set_scene_translate(self, vector: QVector3D):
        self.scene.translate(vector)
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

    def new_cursor_position(self, x: int, y: int):
        pass

    def render_to_image(self, width: int, height: int, transparent_bg: bool = False, crop_to_content: bool = False):
        self.makeCurrent()
        return self.renderer.render_to_image(width, height, transparent_bg, crop_to_content)

    def item_under_cursor(self) -> None | Item:
        self.makeCurrent()
        image = self.renderer.picking_image(self.size().width(), self.size().height())

        x = self._cursor_pos.x()
        y = self._cursor_pos.y()

        color = image.pixelColor(x, y)
        obj_id = color_to_id(color)

        return self.scene.find_item_by_id(obj_id)

