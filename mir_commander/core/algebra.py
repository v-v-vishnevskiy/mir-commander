import math
from typing import Self, Union


class Vector3D:
    __slots__ = ("_x", "_y", "_z")

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    @property
    def data(self) -> tuple[float, float, float]:
        return (self._x, self._y, self._z)

    @property
    def length(self) -> float:
        """Calculate and return the length of the vector."""
        return math.sqrt(self._x * self._x + self._y * self._y + self._z * self._z)

    @property
    def length_squared(self) -> float:
        """Calculate and return the squared length of the vector."""
        return self._x * self._x + self._y * self._y + self._z * self._z

    @property
    def normalized(self) -> "Vector3D":
        """Return a normalized copy of this vector."""
        length = self.length
        if length < 1e-10:
            return Vector3D(0.0, 0.0, 0.0)
        return Vector3D(self._x / length, self._y / length, self._z / length)

    def normalize(self):
        """Normalize this vector in place."""
        length = self.length
        if length >= 1e-10:
            self._x /= length
            self._y /= length
            self._z /= length

    def distance_to_point(self, point: "Vector3D") -> float:
        """Calculate distance to another point."""
        dx = self._x - point._x
        dy = self._y - point._y
        dz = self._z - point._z
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    @staticmethod
    def dot_product(v1: "Vector3D", v2: "Vector3D") -> float:
        """Calculate dot product of two vectors."""
        return v1._x * v2._x + v1._y * v2._y + v1._z * v2._z

    @staticmethod
    def cross_product(v1: "Vector3D", v2: "Vector3D") -> "Vector3D":
        """Calculate cross product of two vectors."""
        return Vector3D(v1._y * v2._z - v1._z * v2._y, v1._z * v2._x - v1._x * v2._z, v1._x * v2._y - v1._y * v2._x)

    def normal(self, v2: "Vector3D", v3: "Vector3D") -> "Vector3D":
        """
        Calculate normal vector for a triangle defined by three points.
        Returns normalized vector perpendicular to the plane.
        """
        edge1 = Vector3D(v2._x - self._x, v2._y - self._y, v2._z - self._z)
        edge2 = Vector3D(v3._x - self._x, v3._y - self._y, v3._z - self._z)
        return Vector3D.cross_product(edge1, edge2).normalized

    def __add__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self._x + other._x, self._y + other._y, self._z + other._z)

    def __sub__(self, other: "Vector3D") -> "Vector3D":
        return Vector3D(self._x - other._x, self._y - other._y, self._z - other._z)

    def __mul__(self, other: Union[float, "Vector3D"]) -> "Vector3D":
        if isinstance(other, Vector3D):
            # Element-wise multiplication
            return Vector3D(self._x * other._x, self._y * other._y, self._z * other._z)
        else:
            # Scalar multiplication
            return Vector3D(self._x * other, self._y * other, self._z * other)

    def __rmul__(self, scalar: float) -> "Vector3D":
        return Vector3D(scalar * self._x, scalar * self._y, scalar * self._z)

    def __truediv__(self, scalar: float) -> "Vector3D":
        return Vector3D(self._x / scalar, self._y / scalar, self._z / scalar)

    def __neg__(self) -> "Vector3D":
        return Vector3D(-self._x, -self._y, -self._z)

    def __iadd__(self, other: "Vector3D") -> Self:
        self._x += other._x
        self._y += other._y
        self._z += other._z
        return self

    def __isub__(self, other: "Vector3D") -> Self:
        self._x -= other._x
        self._y -= other._y
        self._z -= other._z
        return self

    def __imul__(self, other: Union[float, "Vector3D"]) -> Self:
        if isinstance(other, Vector3D):
            # Element-wise multiplication
            self._x *= other._x
            self._y *= other._y
            self._z *= other._z
        else:
            # Scalar multiplication
            self._x *= other
            self._y *= other
            self._z *= other
        return self

    def __itruediv__(self, scalar: float) -> Self:
        self._x /= scalar
        self._y /= scalar
        self._z /= scalar
        return self

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector3D):
            return False
        return math.isclose(self._x, other._x) and math.isclose(self._y, other._y) and math.isclose(self._z, other._z)

    def __repr__(self) -> str:
        return f"Vector3D({self._x}, {self._y}, {self._z})"


class Quaternion:
    __slots__ = ("_w", "_x", "_y", "_z")

    def __init__(self, w: float = 1.0, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self._w = float(w)
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    @property
    def w(self) -> float:
        return self._w

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y

    @property
    def z(self) -> float:
        return self._z

    @property
    def scalar(self) -> float:
        """Return scalar part (w component)."""
        return self._w

    @property
    def vector(self) -> Vector3D:
        """Return vector part (x, y, z components)."""
        return Vector3D(self._x, self._y, self._z)

    @property
    def length(self) -> float:
        """Calculate and return the length of the quaternion."""
        return math.sqrt(self._w * self._w + self._x * self._x + self._y * self._y + self._z * self._z)

    @property
    def normalized(self) -> "Quaternion":
        """Return a normalized copy of this quaternion."""
        length = self.length
        if length < 1e-10:
            return Quaternion(1.0, 0.0, 0.0, 0.0)
        return Quaternion(self._w / length, self._x / length, self._y / length, self._z / length)

    def normalize(self):
        """Normalize this quaternion in place."""
        length = self.length
        if length >= 1e-10:
            self._w /= length
            self._x /= length
            self._y /= length
            self._z /= length

    @staticmethod
    def from_axis_and_angle(axis: Vector3D, angle: float) -> "Quaternion":
        """Create quaternion from axis and angle (in degrees)."""
        rad = math.radians(angle)
        half_angle = rad / 2.0
        s = math.sin(half_angle)

        # Normalize axis
        axis_normalized = axis.normalized

        return Quaternion(
            math.cos(half_angle),
            axis_normalized.x * s,
            axis_normalized.y * s,
            axis_normalized.z * s,
        )

    @staticmethod
    def rotation_to(from_vec: Vector3D, to_vec: Vector3D) -> "Quaternion":
        """Create quaternion that rotates from one vector to another."""
        v1 = from_vec.normalized
        v2 = to_vec.normalized

        dot = Vector3D.dot_product(v1, v2)

        # Vectors are parallel
        if dot >= 0.9999:
            return Quaternion(1.0, 0.0, 0.0, 0.0)

        # Vectors are opposite
        if dot <= -0.9999:
            # Find orthogonal vector
            axis = Vector3D.cross_product(Vector3D(1.0, 0.0, 0.0), v1)
            if axis.length < 0.0001:
                axis = Vector3D.cross_product(Vector3D(0.0, 1.0, 0.0), v1)
            axis = axis.normalized
            return Quaternion(0.0, axis.x, axis.y, axis.z)

        # General case
        axis = Vector3D.cross_product(v1, v2)
        w = math.sqrt(v1.length_squared * v2.length_squared) + dot

        quat = Quaternion(w, axis.x, axis.y, axis.z)
        return quat.normalized

    def to_rotation_matrix(self) -> "Matrix4x4":
        """Convert quaternion to 4x4 rotation matrix (column-major)."""
        # Normalize first
        q = self.normalized
        w, x, y, z = q._w, q._x, q._y, q._z

        matrix = Matrix4x4()

        # Column 0
        matrix._data[0] = 1.0 - 2.0 * (y * y + z * z)
        matrix._data[1] = 2.0 * (x * y + w * z)
        matrix._data[2] = 2.0 * (x * z - w * y)
        matrix._data[3] = 0.0

        # Column 1
        matrix._data[4] = 2.0 * (x * y - w * z)
        matrix._data[5] = 1.0 - 2.0 * (x * x + z * z)
        matrix._data[6] = 2.0 * (y * z + w * x)
        matrix._data[7] = 0.0

        # Column 2
        matrix._data[8] = 2.0 * (x * z + w * y)
        matrix._data[9] = 2.0 * (y * z - w * x)
        matrix._data[10] = 1.0 - 2.0 * (x * x + y * y)
        matrix._data[11] = 0.0

        # Column 3
        matrix._data[12] = 0.0
        matrix._data[13] = 0.0
        matrix._data[14] = 0.0
        matrix._data[15] = 1.0

        return matrix

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        """Quaternion multiplication."""
        w1, x1, y1, z1 = self._w, self._x, self._y, self._z
        w2, x2, y2, z2 = other._w, other._x, other._y, other._z

        return Quaternion(
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quaternion):
            return False
        return (
            math.isclose(self._w, other._w)
            and math.isclose(self._x, other._x)
            and math.isclose(self._y, other._y)
            and math.isclose(self._z, other._z)
        )

    def __repr__(self) -> str:
        return f"Quaternion(w={self._w}, x={self._x}, y={self._y}, z={self._z})"


class Matrix4x4:
    __slots__ = ("_data",)

    def __init__(self):
        # Store as column-major order (OpenGL convention)
        # Memory layout: [m00, m10, m20, m30, m01, m11, m21, m31, m02, m12, m22, m32, m03, m13, m23, m33]
        self._data = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

    @property
    def data(self) -> tuple[float, ...]:
        """Return matrix data as tuple (column-major order)."""
        return tuple(self._data)

    def set_to_identity(self):
        """Set matrix to identity matrix."""
        self._data = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]

    def translate(self, vector: Vector3D):
        """Apply translation to the matrix."""

        translation = Matrix4x4()
        translation._data[12] = vector.x
        translation._data[13] = vector.y
        translation._data[14] = vector.z

        self._data = (self * translation)._data

    def scale(self, vector: Vector3D):
        """Apply scaling to the matrix."""

        scale_matrix = Matrix4x4()
        scale_matrix._data[0] = vector.x
        scale_matrix._data[5] = vector.y
        scale_matrix._data[10] = vector.z

        self._data = (self * scale_matrix)._data

    def rotate(self, angle_or_quat: float | Quaternion, axis: Vector3D | None = None):
        """
        Apply rotation to the matrix.
        Can be called with either (angle, axis) or (quaternion).
        """
        if isinstance(angle_or_quat, Quaternion):
            # Quaternion rotation
            rotation = angle_or_quat.to_rotation_matrix()
        else:
            # Angle and axis rotation
            if axis is None:
                raise ValueError("axis must be provided when rotating by angle")

            rad = math.radians(angle_or_quat)
            c = math.cos(rad)
            s = math.sin(rad)
            t = 1.0 - c

            # Normalize axis
            axis_normalized = axis.normalized
            x = axis_normalized.x
            y = axis_normalized.y
            z = axis_normalized.z

            rotation = Matrix4x4()
            # Column 0
            rotation._data[0] = t * x * x + c
            rotation._data[1] = t * x * y + s * z
            rotation._data[2] = t * x * z - s * y
            # Column 1
            rotation._data[4] = t * x * y - s * z
            rotation._data[5] = t * y * y + c
            rotation._data[6] = t * y * z + s * x
            # Column 2
            rotation._data[8] = t * x * z + s * y
            rotation._data[9] = t * y * z - s * x
            rotation._data[10] = t * z * z + c

        self._data = (self * rotation)._data

    def look_at(self, eye: Vector3D, center: Vector3D, up: Vector3D):
        """Set matrix to look-at transformation."""
        forward = (center - eye).normalized
        side = Vector3D.cross_product(forward, up).normalized
        up_vec = Vector3D.cross_product(side, forward)

        self._data[0] = side.x
        self._data[4] = side.y
        self._data[8] = side.z
        self._data[12] = -Vector3D.dot_product(side, eye)

        self._data[1] = up_vec.x
        self._data[5] = up_vec.y
        self._data[9] = up_vec.z
        self._data[13] = -Vector3D.dot_product(up_vec, eye)

        self._data[2] = -forward.x
        self._data[6] = -forward.y
        self._data[10] = -forward.z
        self._data[14] = Vector3D.dot_product(forward, eye)

        self._data[3] = 0.0
        self._data[7] = 0.0
        self._data[11] = 0.0
        self._data[15] = 1.0

    def perspective(self, fov: float, aspect: float, near_plane: float, far_plane: float):
        """Set matrix to perspective projection."""
        self.set_to_identity()

        rad = math.radians(fov)
        f = 1.0 / math.tan(rad / 2.0)

        self._data[0] = f / aspect
        self._data[5] = f
        self._data[10] = (far_plane + near_plane) / (near_plane - far_plane)
        self._data[11] = -1.0
        self._data[14] = (2.0 * far_plane * near_plane) / (near_plane - far_plane)
        self._data[15] = 0.0

    def ortho(self, left: float, right: float, bottom: float, top: float, near_plane: float, far_plane: float):
        """Set matrix to orthographic projection."""
        self.set_to_identity()

        width = right - left
        height = top - bottom
        depth = far_plane - near_plane

        self._data[0] = 2.0 / width
        self._data[5] = 2.0 / height
        self._data[10] = -2.0 / depth
        self._data[12] = -(right + left) / width
        self._data[13] = -(top + bottom) / height
        self._data[14] = -(far_plane + near_plane) / depth

    def __mul__(self, other: "Matrix4x4") -> "Matrix4x4":
        """Matrix multiplication for column-major matrices."""
        result = Matrix4x4()

        # Column-major: data[col * 4 + row]
        for col in range(4):
            for row in range(4):
                sum_val = 0.0
                for k in range(4):
                    sum_val += self._data[k * 4 + row] * other._data[col * 4 + k]
                result._data[col * 4 + row] = sum_val

        return result

    def __getitem__(self, index: int) -> float:
        """Get matrix element by index."""
        return self._data[index]

    def __setitem__(self, index: int, value: float):
        """Set matrix element by index."""
        self._data[index] = value

    def __repr__(self) -> str:
        return f"Matrix4x4({self._data})"
