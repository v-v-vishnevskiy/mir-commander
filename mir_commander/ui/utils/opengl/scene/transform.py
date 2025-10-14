from PySide6.QtGui import QMatrix4x4, QQuaternion, QVector3D


class Transform:
    __slots__ = ("_matrix", "_scale", "_rotation", "_position", "_dirty")

    def __init__(self):
        self._matrix = QMatrix4x4()
        self._scale = QVector3D(1.0, 1.0, 1.0)
        self._rotation = QQuaternion()
        self._position = QVector3D(0.0, 0.0, 0.0)

        self._dirty = True

    @property
    def matrix(self) -> QMatrix4x4:
        if self._dirty:
            self._update_matrix()
            self._dirty = False
        return self._matrix

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

    def rotate(self, pitch: float, yaw: float, roll: float = 0.0):
        pitch_quat = QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), pitch)
        yaw_quat = QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), yaw)
        roll_quat = QQuaternion.fromAxisAndAngle(QVector3D(0, 0, 1), roll)

        rotation = pitch_quat * yaw_quat * roll_quat
        self._rotation = rotation * self._rotation
        self._dirty = True

    def set_rotation(self, value: QQuaternion):
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
