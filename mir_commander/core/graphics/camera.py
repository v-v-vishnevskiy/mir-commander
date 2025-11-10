import math

from PySide6.QtGui import QMatrix4x4, QVector3D


class Camera:
    """
    Camera class for managing 3D camera position, orientation and view matrix.

    The camera uses a look-at approach where it maintains:
    - position: camera location in world space
    - target: point the camera is looking at
    - up_vector: up direction for camera orientation
    """

    __slots__ = (
        "_position",
        "_target",
        "_up_vector",
        "_movement_speed",
        "_rotation_speed",
        "_zoom_speed",
        "_matrix",
        "_dirty",
    )

    def __init__(
        self,
        position: QVector3D = QVector3D(0.0, 0.0, 1.0),
        target: QVector3D = QVector3D(0.0, 0.0, 0.0),
        up_vector: QVector3D = QVector3D(0.0, 1.0, 0.0),
        movement_speed: float = 1.0,
        rotation_speed: float = 1.0,
        zoom_speed: float = 1.0,
    ):
        """
        Initialize camera with position, target and up vector.

        Args:
            position: Camera position in world space (default: (0, 0, 1))
            target: Point the camera is looking at (default: (0, 0, 0))
            up_vector: Up direction vector (default: (0, 1, 0))
            movement_speed: Speed of camera movement (default: 1.0)
            rotation_speed: Speed of camera rotation (default: 1.0)
            zoom_speed: Speed of camera zoom (default: 1.0)
        """

        self._position = position
        self._target = target
        self._up_vector = up_vector

        # Camera movement parameters
        self._movement_speed = movement_speed
        self._rotation_speed = rotation_speed
        self._zoom_speed = zoom_speed

        self._matrix = QMatrix4x4()
        self._dirty = True

    @property
    def matrix(self) -> QMatrix4x4:
        if self._dirty:
            self._update_matrix()
            self._dirty = False
        return self._matrix

    @property
    def position(self) -> QVector3D:
        return self._position

    def set_position(self, position: QVector3D):
        """Set camera position."""

        self._position = position
        self._dirty = True

    def set_target(self, target: QVector3D):
        """Set camera target point."""

        self._target = target
        self._dirty = True

    def set_up_vector(self, up_vector: QVector3D):
        """Set camera up vector."""

        self._up_vector = up_vector.normalized()
        self._dirty = True

    def look_at(self, position: QVector3D, target: QVector3D, up_vector: None | QVector3D = None):
        """
        Set camera to look at a specific target from a specific position.

        Args:
            position: Camera position
            target: Point to look at
            up_vector: Up direction (optional, uses current if not provided)
        """

        self._position = position
        self._target = target
        if up_vector is not None:
            self._up_vector = up_vector.normalized()
        self._dirty = True

    def translate(self, translation: QVector3D):
        """
        Move camera by translation vector.

        Args:
            translation: Vector to translate camera by
        """

        self._position += translation
        self._target += translation
        self._dirty = True

    def move_forward(self, distance: float):
        """
        Move camera forward along its view direction.

        Args:
            distance: Distance to move (positive = forward, negative = backward)
        """

        direction = (self._target - self._position).normalized()
        translation = direction * distance * self._movement_speed
        self.translate(translation)

    def move_right(self, distance: float):
        """
        Move camera right relative to its orientation.

        Args:
            distance: Distance to move (positive = right, negative = left)
        """

        forward = (self._target - self._position).normalized()
        right = QVector3D.crossProduct(forward, self._up_vector).normalized()
        translation = right * distance * self._movement_speed
        self.translate(translation)

    def move_up(self, distance: float):
        """
        Move camera up relative to its orientation.

        Args:
            distance: Distance to move (positive = up, negative = down)
        """

        translation = self._up_vector * distance * self._movement_speed
        self.translate(translation)

    def orbit_around_target(self, pitch: float, yaw: float):
        """
        Orbit camera around its target point.

        Args:
            pitch: Vertical rotation in degrees (positive = up, negative = down)
            yaw: Horizontal rotation in degrees (positive = right, negative = left)
        """

        # Convert to radians
        pitch_rad = pitch * self._rotation_speed * 0.0174533  # pi/180
        yaw_rad = yaw * self._rotation_speed * 0.0174533

        # Get current distance from target
        distance = (self._position - self._target).length()

        # Calculate new position using spherical coordinates
        current_pitch = self._get_pitch_angle()
        current_yaw = self._get_yaw_angle()

        new_pitch = current_pitch + pitch_rad
        new_yaw = current_yaw + yaw_rad

        # Clamp pitch to avoid gimbal lock
        new_pitch = max(-1.5708, min(1.5708, new_pitch))  # -pi/2 to pi/2

        # Calculate new position
        x = distance * math.cos(new_pitch) * math.sin(new_yaw)
        y = distance * math.sin(new_pitch)
        z = distance * math.cos(new_pitch) * math.cos(new_yaw)

        new_position = self._target + QVector3D(x, y, z)
        self.set_position(new_position)

    def zoom_to_target(self, factor: float):
        """
        Zoom camera towards or away from target.

        Args:
            factor: Zoom factor (positive = zoom in, negative = zoom out)
        """

        direction = (self._target - self._position).normalized()
        distance = (self._target - self._position).length()

        # Calculate new distance
        new_distance = distance * (1.0 + factor * self._zoom_speed)
        new_distance = max(0.1, new_distance)  # Prevent getting too close

        # Calculate new position
        new_position = self._target - direction * new_distance
        self.set_position(new_position)

    def reset_to_default(self):
        """Reset camera to default position and orientation."""

        self.look_at(
            position=QVector3D(0.0, 0.0, 1.0), target=QVector3D(0.0, 0.0, 0.0), up_vector=QVector3D(0.0, 1.0, 0.0)
        )

    def get_direction(self) -> QVector3D:
        """Get camera view direction (normalized vector from position to target)."""

        return (self._target - self._position).normalized()

    def get_right_vector(self) -> QVector3D:
        """Get camera right vector (normalized)."""

        forward = self.get_direction()
        return QVector3D.crossProduct(forward, self._up_vector).normalized()

    def get_distance_to_target(self) -> float:
        """Get distance from camera to target."""

        return (self._target - self._position).length()

    def get_distance_to_point(self, point: QVector3D) -> float:
        """Get distance from camera to a point."""

        return self._position.distanceToPoint(point)

    def _get_pitch_angle(self) -> float:
        """Get current pitch angle in radians."""

        direction = self.get_direction()
        return math.asin(direction.y())

    def _get_yaw_angle(self) -> float:
        """Get current yaw angle in radians."""

        direction = self.get_direction()
        return math.atan2(direction.x(), direction.z())

    def _update_matrix(self):
        """Update the view matrix based on current camera parameters."""

        self._matrix.setToIdentity()
        self._matrix.lookAt(self._position, self._target, self._up_vector)

    def __repr__(self) -> str:
        return f"Camera(position={self._position}, target={self._target})"
