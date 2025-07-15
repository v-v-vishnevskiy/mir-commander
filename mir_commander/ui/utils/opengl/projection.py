import logging
from abc import ABC, abstractmethod

from PySide6.QtGui import QMatrix4x4

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


class PerspectiveProjection(AbstractProjection):
    def __init__(self, fov: float = 45.0, near_plane: float = 0.1, far_plane: float = 1000.0):
        super().__init__()
        self._fov = fov
        self._near_plane = near_plane
        self._far_plane = far_plane

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

    def build_projections(self, width: int, height: int):
        self.perspective_projection.setup_projection(width, height)
        self.orthographic_projection.setup_projection(width, height)

    def set_projection_mode(self, mode: ProjectionMode):
        if self._projection_mode == mode:
            return
        self._projection_mode = mode
        logger.debug("Setting projection mode to %s", mode.name)

    def toggle_projection_mode(self):
        if self._projection_mode == ProjectionMode.Orthographic:
            self.set_projection_mode(ProjectionMode.Perspective)
        else:
            self.set_projection_mode(ProjectionMode.Orthographic)
