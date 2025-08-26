from ctypes import c_void_p

import numpy as np
from pydantic_extra_types.color import Color
from PySide6.QtCore import QRect
from PySide6.QtGui import QColor, QImage, QVector3D

Color4f = tuple[float, float, float, float]
null = c_void_p(0)


def normalize_color(value: Color) -> Color4f:
    """
    Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
    """

    r, g, b = value.as_rgb_tuple()  # type: ignore[misc]
    return r / 255, g / 255, b / 255, 1.0


def color_to_qcolor(value: Color, alpha: bool = True) -> QColor:
    r, g, b, a = value.as_rgb_tuple(alpha=True)  # type: ignore[misc]
    return QColor(r, g, b, int(a * 255) if alpha else 255)


def color_to_color4f(value: Color, alpha: bool = True) -> Color4f:
    r, g, b, a = value.as_rgb_tuple(alpha=True)  # type: ignore[misc]
    return r / 255, g / 255, b / 255, a if alpha else 1.0


def id_to_color(obj_id: int) -> Color4f:
    # Supports up to 256³ = 16,777,216 objects
    r = ((obj_id >> 16) & 0xFF) / 255.0
    g = ((obj_id >> 8) & 0xFF) / 255.0
    b = (obj_id & 0xFF) / 255.0
    return (r, g, b, 1.0)


def color_to_id(color: QColor) -> int:
    r = int(color.red())
    g = int(color.green())
    b = int(color.blue())
    return b | (g << 8) | (r << 16)


def compute_vertex_normals(vertices: np.ndarray) -> np.ndarray:
    normals = []
    for i in range(0, len(vertices), 3):
        norm = QVector3D(*vertices[i : i + 3])
        norm.normalize()
        normals.extend([norm.x(), norm.y(), norm.z()])
    return np.array(normals, dtype=np.float32)


def compute_face_normals(vertices: np.ndarray) -> np.ndarray:
    normals: list[float] = []
    for i in range(0, len(vertices), 9):
        normal = QVector3D().normal(
            QVector3D(*vertices[i : i + 3]),
            QVector3D(*vertices[i + 3 : i + 6]),
            QVector3D(*vertices[i + 6 : i + 9]),
        )
        normals.extend([normal.x(), normal.y(), normal.z()] * 3)
    return np.array(normals, dtype=np.float32)


def crop_image_to_content(image: QImage, bg_color: QColor) -> QImage:
    xmin = ymin = xmax = ymax = -1

    for y in range(image.height()):
        for x in range(image.width()):
            if image.pixelColor(x, y) != bg_color:
                ymin = y
                break
        if ymin >= 0:
            break

    for y in reversed(range(image.height())):
        for x in range(image.width()):
            if image.pixelColor(x, y) != bg_color:
                ymax = y
                break
        if ymax >= 0:
            break

    for x in range(image.width()):
        for y in range(image.height()):
            if image.pixelColor(x, y) != bg_color:
                xmin = x
                break
        if xmin >= 0:
            break

    for x in reversed(range(image.width())):
        for y in range(image.height()):
            if image.pixelColor(x, y) != bg_color:
                xmax = x
                break
        if xmax >= 0:
            break

    if xmin >= 0 and xmax >= 0 and ymin >= 0 and ymax >= 0:
        crop_area = QRect(xmin, ymin, xmax - xmin + 1, ymax - ymin + 1)
        image = image.copy(crop_area)

    return image
