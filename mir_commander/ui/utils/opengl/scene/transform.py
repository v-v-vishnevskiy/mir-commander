from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D


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

    def __init__(self):
        self._matrix = QMatrix4x4()
        self._scale = QVector3D(1.0, 1.0, 1.0)
        self._rotation = QQuaternion()
        self._position = QVector3D(0.0, 0.0, 0.0)
        self._pitch = 0.0
        self._yaw = 0.0
        self._roll = 0.0

        self._dirty = True

    @property
    def matrix(self) -> QMatrix4x4:
        if self._dirty:
            self._update_matrix()
            self._dirty = False
        return self._matrix

    @property
    def rotation(self) -> QQuaternion:
        return self._rotation

    @property
    def rotation_angles(self) -> tuple[float, float, float]:
        return (self._pitch, self._yaw, self._roll)

    @property
    def position(self) -> QVector3D:
        return QVector3D(self._position)

    @property
    def dirty(self) -> int:
        return self._dirty

    def _update_matrix(self):
        self._matrix.setToIdentity()
        self._matrix.translate(self._position)
        self._matrix.rotate(self._rotation)
        self._matrix.scale(self._scale)

    def scale(self, value: QVector3D):
        self._scale *= value
        self._dirty = True

    def set_scale(self, value: QVector3D):
        self._scale = value
        self._dirty = True

    def rotate(self, pitch: float, yaw: float, roll: float):
        self._pitch = normalize_angle(self._pitch + pitch)
        self._yaw = normalize_angle(self._yaw + yaw)
        self._roll = normalize_angle(self._roll + roll)

        pitch_quat = QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), pitch)
        yaw_quat = QQuaternion.fromAxisAndAngle(QVector3D(0.0, 1.0, 0.0), yaw)
        roll_quat = QQuaternion.fromAxisAndAngle(QVector3D(0.0, 0.0, 1.0), roll)

        self._rotation = pitch_quat * yaw_quat * roll_quat * self._rotation
        self._dirty = True

    def set_rotation(self, pitch: float, yaw: float, roll: float):
        self._pitch = normalize_angle(pitch)
        self._yaw = normalize_angle(yaw)
        self._roll = normalize_angle(roll)

        pitch_quat = QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), pitch)
        yaw_quat = QQuaternion.fromAxisAndAngle(QVector3D(0.0, 1.0, 0.0), yaw)
        roll_quat = QQuaternion.fromAxisAndAngle(QVector3D(0.0, 0.0, 1.0), roll)

        self._rotation = pitch_quat * yaw_quat * roll_quat
        self._dirty = True

    def set_q_rotation(self, value: QQuaternion):
        self._rotation = value
        self._dirty = True

    def translate(self, value: QVector3D):
        self._position += value
        self._dirty = True

    def set_position(self, value: QVector3D):
        self._position = value
        self._dirty = True

    def __repr__(self):
        return f"Transform(scale={self._scale}, rotation={self._rotation}, position={self._position})"
