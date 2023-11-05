from enum import Enum
from typing import Callable

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QIcon, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from mir_commander.ui.utils.opengl.keymap import Keymap
from mir_commander.ui.utils.opengl.scene import Scene


class ClickAndMoveMode(Enum):
    Nothing = 0
    Rotation = 1


class WheelMode(Enum):
    Nothing = 0
    Scale = 1


class Widget(QOpenGLWidget):
    def __init__(self, scene: None | Scene = None, keymap: None | Keymap = None, parent: None | QWidget = None):
        super().__init__(parent)
        self.__mouse_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale
        self._scene = scene or Scene(self)
        self._keymap = keymap or Keymap(
            id(self),
            {
                "rotate_down": ["down"],
                "rotate_left": ["left"],
                "rotate_right": ["right"],
                "rotate_up": ["up"],
                "toggle_projection": ["p"],
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

    def _init_actions(self):
        self._actions["rotate_down"] = (True, self._scene.rotate, (1, 0))
        self._actions["rotate_left"] = (True, self._scene.rotate, (0, 1))
        self._actions["rotate_right"] = (True, self._scene.rotate, (0, -1))
        self._actions["rotate_up"] = (True, self._scene.rotate, (-1, 0))
        self._actions["toggle_projection"] = (False, self._scene.toggle_projection_mode, tuple())
        self._actions["zoom_in"] = (True, self._scene.scale, (-0.015,))
        self._actions["zoom_out"] = (True, self._scene.scale, (0.015,))

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

    @property
    def mouse_pos(self) -> tuple[int, int]:
        return self.__mouse_pos.x(), self.__mouse_pos.y()

    def resize(self, w: int, h: int):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.resize(w, h)
        else:
            super().resize(w, h)

    def setWindowIcon(self, icon: QIcon):
        parent = self.parent()
        if isinstance(parent, QMdiSubWindow):
            parent.setWindowIcon(icon)
        else:
            super().setWindowIcon(icon)

    def initializeGL(self):
        self._scene.initialize_gl()

    def paintGL(self):
        self._scene.paint()

    def resizeGL(self, w: int, h: int):
        self._scene.update_window_size()

    def keyPressEvent(self, event: QKeyEvent):
        self._call_action(event, self._keymap.match_key_event)

    def keyReleaseEvent(self, event: QKeyEvent):
        self._stop_action(event, self._keymap.match_key_event)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position()
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._click_and_move_mode == ClickAndMoveMode.Rotation:
                diff = pos - self.__mouse_pos
                self._scene.rotate(diff.y(), -diff.x())
        else:
            self._scene.move_cursor(pos.x(), pos.y())

        self.__mouse_pos = pos

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
