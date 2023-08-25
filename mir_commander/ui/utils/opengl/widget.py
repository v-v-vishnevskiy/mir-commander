from enum import Enum

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QWidget

from mir_commander.ui.utils.opengl.scene import Scene


class ClickAndMoveMode(Enum):
    Nothing = 0
    Rotation = 1


class WheelMode(Enum):
    Nothing = 0
    Scale = 1


class Widget(QOpenGLWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.__mouse_pos: QPoint = QPoint(0, 0)
        self._click_and_move_mode = ClickAndMoveMode.Rotation
        self._wheel_mode = WheelMode.Scale
        self._scene = Scene(self)

    def paintGL(self):
        self._scene.paint()

    def resizeGL(self, w: int, h: int):
        self._scene.update_window_size()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._click_and_move_mode == ClickAndMoveMode.Rotation:
                diff = event.position() - self.__mouse_pos
                self._scene.rotate(diff.y(), -diff.x())

        self.__mouse_pos = event.position()

    def mousePressEvent(self, event: QMouseEvent):
        pass

    def wheelEvent(self, event: QWheelEvent):
        if self._wheel_mode == WheelMode.Scale:
            delta = event.angleDelta().y()
            if delta > 0:
                self._scene.scale(1.1)
            elif delta < 0:
                self._scene.scale(0.9)
