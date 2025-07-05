from ctypes import c_void_p
from pydantic_extra_types.color import Color

Color4f = tuple[float, float, float, float]
null = c_void_p(0)


def normalize_color(value: Color) -> Color4f:
    """
    Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
    """

    r, g, b = value.as_rgb_tuple()
    return r / 255, g / 255, b / 255, 1.0
