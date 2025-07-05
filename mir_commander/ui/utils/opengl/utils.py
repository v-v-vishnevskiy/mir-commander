from ctypes import c_void_p
from pydantic_extra_types.color import Color
from PySide6.QtGui import QColor


Color4f = tuple[float, float, float, float]
null = c_void_p(0)


def normalize_color(value: Color) -> Color4f:
    """
    Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
    """

    r, g, b = value.as_rgb_tuple()
    return r / 255, g / 255, b / 255, 1.0


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
