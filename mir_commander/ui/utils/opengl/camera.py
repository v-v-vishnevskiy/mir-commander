from OpenGL.GL import (
    GL_MODELVIEW,
    GL_PROJECTION,
    glLoadMatrixf,
    glMatrixMode,
    glViewport,
)
from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D

from .enums import ProjectionMode


class Camera:
    def __init__(self):
        self._translation_matrix = QMatrix4x4()
        self._projection_matrix = QMatrix4x4()
        self._projection_mode = ProjectionMode.Orthographic
        self._fov = 45.0
        self._near_plane = 0.001
        self._far_plane = 10000.0
        self._camera_distance = 10.0
        self._center = QVector3D()
        self._rotation = QQuaternion()

    def setup_projection_matrix(self, width: int, height: int):
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

        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self._projection_matrix.data())
        glMatrixMode(GL_MODELVIEW)

    def setup_translation_matrix(self):
        matrix = self._translation_matrix
        matrix.setToIdentity()
        matrix.translate(0.0, 0.0, -self._camera_distance * 3.6)
        matrix.rotate(self._rotation)
        matrix.translate(-self._center)

    def set_projection_mode(self, mode: ProjectionMode | str):
        if isinstance(mode, str):
            if mode == "perspective":
                mode = ProjectionMode.Perspective
            elif mode == "orthographic":
                mode = ProjectionMode.Orthographic
            else:
                raise RuntimeError(f"Invalid projection mode: {mode}")
        self._projection_mode = mode

    def toggle_projection_mode(self):
        if self._projection_mode == ProjectionMode.Orthographic:
            self.set_projection_mode(ProjectionMode.Perspective)
        else:
            self.set_projection_mode(ProjectionMode.Orthographic)

    def set_fov(self, value: float):
        self._fov = min(90.0, max(35.0, value))

    def set_far_plane(self, value: float):
        self._far_plane = max(500.0, value)

    def set_position(self, point: QVector3D):
        self._center = point
        self.setup_translation_matrix()

    def set_camera_distance(self, distance: float):
        self._camera_distance = distance
        self.setup_translation_matrix()

    def rotate(self, pitch: float, yaw: float, roll: float = 0.0, rotation_speed: float = 1.0):
        r = QQuaternion.fromEulerAngles(pitch * rotation_speed, -yaw * rotation_speed, roll * rotation_speed)
        r *= self._rotation
        self._rotation = r
        self.setup_translation_matrix()

    def scale(self, factor: float, scale_speed: float = 1.0):
        self._camera_distance += (factor * scale_speed) * self._camera_distance
        self.setup_translation_matrix()

    @property
    def translation_matrix(self) -> QMatrix4x4:
        return self._translation_matrix

    @property
    def projection_matrix(self) -> QMatrix4x4:
        return self._projection_matrix
