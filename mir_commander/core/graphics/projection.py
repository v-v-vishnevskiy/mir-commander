import math
from abc import ABC, abstractmethod
from enum import Enum

from mir_commander.core.algebra import Matrix4x4


class ProjectionMode(Enum):
    Orthographic = 1
    Perspective = 2


class AbstractProjection(ABC):
    """Base abstract projection class."""

    def __init__(self):
        self.matrix = Matrix4x4()

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
        self._left = 0.0
        self._right = 0.0
        self._bottom = 0.0
        self._top = 0.0

    def setup_projection(self, width: int, height: int):
        """Setup perspective projection matrix with proper aspect ratio handling."""
        self._aspect = width / height

        # Calculate effective FOV and frustum planes based on orientation
        half_fov_rad = math.radians(self._fov / 2.0)
        tan_half_fov = math.tan(half_fov_rad)

        if width <= height:
            # Portrait or square viewport: FOV applies to horizontal axis (narrower)
            # Calculate vertical FOV from horizontal FOV to maintain proper scaling
            effective_fov = math.degrees(2.0 * math.atan(tan_half_fov / self._aspect))

            self._right = self._near_plane * tan_half_fov
            self._left = -self._right
            self._top = self._right / self._aspect
            self._bottom = -self._top
        else:
            # Landscape viewport: FOV applies to vertical axis (standard behavior)
            effective_fov = self._fov

            self._top = self._near_plane * tan_half_fov
            self._bottom = -self._top
            self._right = self._top * self._aspect
            self._left = -self._right

        self.matrix.set_to_identity()
        self.matrix.perspective(effective_fov, self._aspect, self._near_plane, self._far_plane)

    def get_fov(self):
        return self._fov

    def set_fov(self, value: float):
        self._fov = min(90.0, max(35.0, value))

    def set_near_far_plane(self, near_plane: float, far_plane: float):
        if near_plane >= far_plane:
            raise ValueError("Near plane must be less than far plane")
        self._near_plane = near_plane
        self._far_plane = far_plane

    @property
    def frustum_planes(self) -> tuple[float, float, float, float, float, float]:
        return self._left, self._right, self._bottom, self._top, self._near_plane, self._far_plane


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

        self.matrix.set_to_identity()
        self.matrix.ortho(self._left, self._right, self._bottom, self._top, self._near, self._far)

    def set_view_bounds(self, value: float):
        if value <= 0.0:
            raise ValueError("View bounds must be greater than 0.0")
        self._view_bounds = value

    def set_depth_factor(self, value: float):
        if value <= 0.0:
            raise ValueError("Depth factor must be greater than 0.0")
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

    def toggle_projection_mode(self):
        if self._projection_mode == ProjectionMode.Orthographic:
            self.set_projection_mode(ProjectionMode.Perspective)
        else:
            self.set_projection_mode(ProjectionMode.Orthographic)
