import logging
from abc import ABC, abstractmethod

from OpenGL.GL import (
    GL_MODELVIEW,
    GL_PROJECTION,
    glLoadMatrixf,
    glMatrixMode,
    glViewport,
)
from PySide6.QtCore import QRect, QPoint
from PySide6.QtGui import QMatrix4x4, QVector3D

from .enums import ProjectionMode

logger = logging.getLogger("OpenGL.Projection")


class AbstractProjection(ABC):
    """Base abstract projection class."""

    def __init__(self):
        self.matrix = QMatrix4x4()

    @abstractmethod
    def setup_projection(self, width: int, height: int):
        """Implementation specific projection matrix setup."""
        pass

    @abstractmethod
    def _get_near_far_planes(self) -> tuple[float, float]:
        """Get near and far plane values for unprojection calculations."""
        pass

    def point_to_line(self, point: QPoint, viewport: QRect, model_view: QMatrix4x4) -> tuple[QVector3D, QVector3D]:
        x = point.x()
        y = viewport.height() - point.y()  # opengl computes from left-bottom corner

        # Get near and far plane values for unprojection calculations
        near_plane, far_plane = self._get_near_far_planes()

        near_point = QVector3D(x, y, near_plane).unproject(model_view, self.matrix, viewport)
        far_point = QVector3D(x, y, far_plane).unproject(model_view, self.matrix, viewport)

        # Return the near point and the direction vector from near to far
        return near_point, far_point - near_point


class PerspectiveProjection(AbstractProjection):
    def __init__(self, fov: float = 45.0, near_plane: float = 0.001, far_plane: float = 10000.0):
        super().__init__()
        self._fov = fov
        self._near_plane = near_plane
        self._far_plane = far_plane

    def _get_near_far_planes(self) -> tuple[float, float]:
        """Get near and far planes for perspective projection."""
        return -1.0, 1.0

    def setup_projection(self, width: int, height: int):
        """Setup perspective projection matrix."""
        self.matrix.setToIdentity()
        self.matrix.perspective(self._fov, width / height, self._near_plane, self._far_plane)

    def set_fov(self, value: float):
        self._fov = min(90.0, max(35.0, value))


class OrthographicProjection(AbstractProjection):
    def __init__(self, view_bounds: float = 5.4, depth_factor: float = 10.0):
        super().__init__()
        self._view_bounds = view_bounds
        self._orthographic_depth_factor = max(500.0, depth_factor)

    def _get_near_far_planes(self) -> tuple[float, float]:
        depth_range = self._view_bounds * self._orthographic_depth_factor
        return -depth_range, depth_range

    def setup_projection(self, width: int, height: int):
        """Setup orthographic projection matrix with proper aspect ratio handling."""

        # Handle aspect ratio to maintain proper proportions
        if width <= height:
            # Portrait or square viewport
            left = -self._view_bounds
            right = self._view_bounds
            bottom = -self._view_bounds * (height / width)
            top = self._view_bounds * (height / width)
        else:
            # Landscape viewport
            left = -self._view_bounds * (width / height)
            right = self._view_bounds * (width / height)
            bottom = -self._view_bounds
            top = self._view_bounds

        # Calculate depth range for near/far planes
        depth_range = self._view_bounds * self._orthographic_depth_factor

        self.matrix.setToIdentity()
        self.matrix.ortho(left, right, bottom, top, -depth_range, depth_range)

    def set_depth_factor(self, value: float):
        self._orthographic_depth_factor = value


class ProjectionManager:
    def __init__(self, width: int, height: int, projection_mode: ProjectionMode = ProjectionMode.Perspective):
        self._width = width
        self._height = height
        self._projection_mode = projection_mode
        self.perspective_projection = PerspectiveProjection()
        self.perspective_projection.setup_projection(width, height)
        self.orthographic_projection = OrthographicProjection()
        self.orthographic_projection.setup_projection(width, height)

    @property
    def projection_mode(self) -> ProjectionMode:
        return self._projection_mode

    @property
    def active_projection(self) -> AbstractProjection:
        if self._projection_mode == ProjectionMode.Perspective:
            return self.perspective_projection
        return self.orthographic_projection

    def setup_projection(self):
        glViewport(0, 0, self._width, self._height)
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self.active_projection.matrix.data())
        glMatrixMode(GL_MODELVIEW)

    def build_projections(self, width: int, height: int):
        self._width = width
        self._height = height
        self.perspective_projection.setup_projection(width, height)
        self.orthographic_projection.setup_projection(width, height)
        self.setup_projection()

    def set_projection_mode(self, mode: ProjectionMode):
        if self._projection_mode == mode:
            return
        self._projection_mode = mode
        self.setup_projection()
        logger.debug("Setting projection mode to %s", mode.name)

    def toggle_projection_mode(self):
        if self._projection_mode == ProjectionMode.Orthographic:
            self.set_projection_mode(ProjectionMode.Perspective)
        else:
            self.set_projection_mode(ProjectionMode.Orthographic)

    def point_to_line(self, point: QPoint, model_view: QMatrix4x4) -> tuple[QVector3D, QVector3D]:
        return self.active_projection.point_to_line(
            point=point, 
            viewport=QRect(0, 0, self._width, self._height), 
            model_view=model_view
        )
