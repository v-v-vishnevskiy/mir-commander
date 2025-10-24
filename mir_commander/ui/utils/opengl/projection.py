import logging
import math
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

    @property
    @abstractmethod
    def frustum_planes(self) -> tuple[float, float, float, float, float, float]:
        """Implementation specific frustum planes."""
        pass


class PerspectiveProjection(AbstractProjection):
    def __init__(self, fov: float = 45.0, near_plane: float = 0.1, far_plane: float = 1000.0):
        super().__init__()
        self._fov = fov
        self._near_plane = near_plane
        self._far_plane = far_plane
        self._aspect = 1.0

    def setup_projection(self, width: int, height: int):
        """Setup perspective projection matrix."""
        self._aspect = width / height
        self.matrix.setToIdentity()
        self.matrix.perspective(self._fov, self._aspect, self._near_plane, self._far_plane)

    def get_fov(self):
        return self._fov

    def set_fov(self, value: float):
        self._fov = min(90.0, max(35.0, value))

    def set_near_far_plane(self, near_plane: float, far_plane: float):
        self._near_plane = near_plane
        self._far_plane = far_plane

    @property
    def frustum_planes(self) -> tuple[float, float, float, float, float, float]:
        half_fov_rad = math.radians(self._fov / 2.0)
        tan_half_fov = math.tan(half_fov_rad)
        top = self._near_plane * tan_half_fov
        bottom = -top
        right = top * self._aspect
        left = -right
        return left, right, bottom, top, self._near_plane, self._far_plane


class OrthographicProjection(AbstractProjection):
    def __init__(self, view_bounds: float = 10.0, depth_factor: float = 10.0):
        super().__init__()
        self._view_bounds = view_bounds
        self._orthographic_depth_factor = depth_factor
        self._left = -view_bounds
        self._right = view_bounds
        self._bottom = -view_bounds
        self._top = view_bounds
        self._near = -view_bounds * depth_factor
        self._far = view_bounds * depth_factor

    def setup_projection(self, width: int, height: int):
        """Setup orthographic projection matrix with proper aspect ratio handling."""

        # Handle aspect ratio to maintain proper proportions
        if width <= height:
            # Portrait or square viewport
            self._left = -self._view_bounds
            self._right = self._view_bounds
            self._bottom = -self._view_bounds * (height / width)
            self._top = self._view_bounds * (height / width)
        else:
            # Landscape viewport
            self._left = -self._view_bounds * (width / height)
            self._right = self._view_bounds * (width / height)
            self._bottom = -self._view_bounds
            self._top = self._view_bounds

        # Calculate depth range for near/far planes
        depth_range = self._view_bounds * self._orthographic_depth_factor
        self._near = -depth_range
        self._far = depth_range

        self.matrix.setToIdentity()
        self.matrix.ortho(self._left, self._right, self._bottom, self._top, self._near, self._far)

    def set_view_bounds(self, value: float):
        self._view_bounds = value

    def set_depth_factor(self, value: float):
        self._orthographic_depth_factor = value

    @property
    def frustum_planes(self) -> tuple[float, float, float, float, float, float]:
        return self._left, self._right, self._bottom, self._top, self._near, self._far


class ProjectionManager:
    def __init__(self, width: int, height: int, projection_mode: ProjectionMode = ProjectionMode.Perspective):
        self._projection_mode = projection_mode
        self.perspective_projection = PerspectiveProjection()
        self.perspective_projection.setup_projection(width, height)
        self.orthographic_projection = OrthographicProjection()
        self.orthographic_projection.setup_projection(width, height)
        self.build_projections(width, height)

    @property
    def projection_mode(self) -> ProjectionMode:
        return self._projection_mode

    @property
    def active_projection(self) -> AbstractProjection:
        if self._projection_mode == ProjectionMode.Perspective:
            return self.perspective_projection
        return self.orthographic_projection

    @property
    def frustum_planes(self) -> tuple[float, float, float, float, float, float]:
        return self.active_projection.frustum_planes

    def build_projections(self, width: int, height: int):
        self.perspective_projection.setup_projection(width, height)
        self.orthographic_projection.setup_projection(width, height)

    def set_projection_mode(self, mode: ProjectionMode):
        if self._projection_mode == mode:
            return
        self._projection_mode = mode
        logger.info("Setting projection mode to %s", mode.name)

    def toggle_projection_mode(self):
        if self._projection_mode == ProjectionMode.Orthographic:
            self.set_projection_mode(ProjectionMode.Perspective)
        else:
            self.set_projection_mode(ProjectionMode.Orthographic)
