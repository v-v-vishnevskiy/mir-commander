from enum import Enum

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QIcon, QKeyEvent, QMouseEvent, QWheelEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QMdiSubWindow, QWidget

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

        self.setMouseTracking(True)

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

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
        key = event.key()
        if key == Qt.Key_Left:
            self._scene.rotate(0, 10)
        elif key == Qt.Key_Right:
            self._scene.rotate(0, -10)
        elif key == Qt.Key_Up:
            self._scene.rotate(10, 0)
        elif key == Qt.Key_Down:
            self._scene.rotate(-10, 0)
        elif key == Qt.Key_P:
            self._scene.toggle_projection_mode()

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
        pass

    def wheelEvent(self, event: QWheelEvent):
        if self._wheel_mode == WheelMode.Scale:
            delta = event.angleDelta().y()
            if delta > 0:
                self._scene.scale(1.1)
            elif delta < 0:
                self._scene.scale(0.9)
