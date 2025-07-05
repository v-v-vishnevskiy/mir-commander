import logging
import math

from PySide6.QtGui import QMatrix4x4, QVector3D

logger = logging.getLogger("OpenGL.Camera")


class Camera:
    """
    Camera class for managing 3D camera position, orientation and view matrix.
    
    The camera uses a look-at approach where it maintains:
    - position: camera location in world space
    - target: point the camera is looking at
    - up_vector: up direction for camera orientation
    """
    
    def __init__(self, position: None | QVector3D = None, target: None | QVector3D = None, up_vector: None | QVector3D = None):
        """
        Initialize camera with position, target and up vector.
        
        Args:
            position: Camera position in world space (default: (0, 0, 5))
            target: Point the camera is looking at (default: (0, 0, 0))
            up_vector: Up direction vector (default: (0, 1, 0))
        """
        self._position = position or QVector3D(0.0, 0.0, 5.0)
        self._target = target or QVector3D(0.0, 0.0, 0.0)
        self._up_vector = up_vector or QVector3D(0.0, 1.0, 0.0)

        # Camera movement parameters
        self._movement_speed = 1.0
        self._rotation_speed = 1.0
        self._zoom_speed = 1.0
        
        # Initialize view matrix
        self.view_matrix = QMatrix4x4()
        self._update_view_matrix()
    
    def set_position(self, position: QVector3D):
        """Set camera position."""
        self._position = position
        self._update_view_matrix()
    
    def set_target(self, target: QVector3D):
        """Set camera target point."""
        self._target = target
        self._update_view_matrix()
    
    def set_up_vector(self, up_vector: QVector3D):
        """Set camera up vector."""
        self._up_vector = up_vector.normalized()
        self._update_view_matrix()
    
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
        self._update_view_matrix()
    
    def translate(self, translation: QVector3D):
        """
        Move camera by translation vector.
        
        Args:
            translation: Vector to translate camera by
        """
        self._position += translation
        self._target += translation
        self._update_view_matrix()
    
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
            position=QVector3D(0.0, 0.0, 5.0),
            target=QVector3D(0.0, 0.0, 0.0),
            up_vector=QVector3D(0.0, 1.0, 0.0)
        )
        logger.debug("Camera reset to default")
    
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
    
    def _get_pitch_angle(self) -> float:
        """Get current pitch angle in radians."""
        direction = self.get_direction()
        return math.asin(direction.y())
    
    def _get_yaw_angle(self) -> float:
        """Get current yaw angle in radians."""
        direction = self.get_direction()
        return math.atan2(direction.x(), direction.z())
    
    def _update_view_matrix(self):
        """Update the view matrix based on current camera parameters."""
        self.view_matrix.setToIdentity()
        self.view_matrix.lookAt(self._position, self._target, self._up_vector)
    
    def __repr__(self) -> str:
        return f"Camera(pos={self._position}, target={self._target})"
