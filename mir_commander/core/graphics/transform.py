from mir_commander.core.algebra import Matrix4x4, Quaternion, Vector3D


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to range [-180, 180].

    Examples:
        185.0 -> -175.0
        -185.0 -> 175.0
        370.0 -> 10.0
        -370.0 -> -10.0
    """
    if angle < -180:
        angle += int(angle / -180) * 180
    elif angle > 180:
        angle -= int(angle / 180) * 180
    return angle


class Transform:
    __slots__ = ("_matrix", "_scale", "_rotation", "_position", "_dirty", "_pitch", "_yaw", "_roll")

    def __init__(
        self,
        position: Vector3D = Vector3D(0.0, 0.0, 0.0),
        scale: Vector3D = Vector3D(1.0, 1.0, 1.0),
        rotation: Quaternion = Quaternion(),
    ):
        self._matrix = Matrix4x4()
        self._scale = scale
        self._rotation = rotation
        self._position = position
        self._pitch = 0.0
        self._yaw = 0.0
        self._roll = 0.0

        self._dirty = True

    @property
    def matrix(self) -> Matrix4x4:
        if self._dirty:
            self._update_matrix()
            self._dirty = False
        return self._matrix

    @property
    def rotation(self) -> Quaternion:
        return self._rotation

    @property
    def rotation_angles(self) -> tuple[float, float, float]:
        return (self._pitch, self._yaw, self._roll)

    @property
    def position(self) -> Vector3D:
        return self._position

    @property
    def dirty(self) -> int:
        return self._dirty

    def _update_matrix(self):
        self._matrix.set_to_identity()
        self._matrix.translate(self._position)
        self._matrix.rotate(self._rotation)
        self._matrix.scale(self._scale)

    def get_scale(self) -> Vector3D:
        return self._scale

    def scale(self, value: Vector3D):
        self._scale *= value
        self._dirty = True

    def set_scale(self, value: Vector3D):
        self._scale = value
        self._dirty = True

    def rotate(self, pitch: float, yaw: float, roll: float):
        self._pitch = normalize_angle(self._pitch + pitch)
        self._yaw = normalize_angle(self._yaw + yaw)
        self._roll = normalize_angle(self._roll + roll)

        pitch_quat = Quaternion.from_axis_and_angle(Vector3D(1.0, 0.0, 0.0), pitch)
        yaw_quat = Quaternion.from_axis_and_angle(Vector3D(0.0, 1.0, 0.0), yaw)
        roll_quat = Quaternion.from_axis_and_angle(Vector3D(0.0, 0.0, 1.0), roll)

        self._rotation = pitch_quat * yaw_quat * roll_quat * self._rotation
        self._dirty = True

    def set_rotation(self, pitch: float, yaw: float, roll: float):
        self._pitch = normalize_angle(pitch)
        self._yaw = normalize_angle(yaw)
        self._roll = normalize_angle(roll)

        pitch_quat = Quaternion.from_axis_and_angle(Vector3D(1.0, 0.0, 0.0), pitch)
        yaw_quat = Quaternion.from_axis_and_angle(Vector3D(0.0, 1.0, 0.0), yaw)
        roll_quat = Quaternion.from_axis_and_angle(Vector3D(0.0, 0.0, 1.0), roll)

        self._rotation = pitch_quat * yaw_quat * roll_quat
        self._dirty = True

    def set_q_rotation(self, value: Quaternion):
        self._rotation = value
        self._dirty = True

    def translate(self, value: Vector3D):
        self._position += value
        self._dirty = True

    def set_position(self, value: Vector3D):
        self._position = value
        self._dirty = True

    def __repr__(self):
        return f"Transform(scale={self._scale}, rotation={self._rotation}, position={self._position})"
