from ctypes import c_void_p

import numpy as np
from pydantic_extra_types.color import Color
from PySide6.QtGui import QColor

from mir_commander.core.algebra import Vector3D

Color4f = tuple[float, float, float, float]
null = c_void_p(0)


def normalize_color(value: Color) -> Color4f:
    """
    Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
    """

    r, g, b = value.as_rgb_tuple()  # type: ignore[misc]
    return round(r / 255, 4), round(g / 255, 4), round(b / 255, 4), 1.0


def color_to_qcolor(value: Color, alpha: bool = True) -> QColor:
    r, g, b, a = value.as_rgb_tuple(alpha=True)  # type: ignore[misc]
    return QColor(r, g, b, round(a * 255) if alpha else 255)


def color4f_to_qcolor(value: Color4f) -> QColor:
    return QColor(*[round(c * 255) for c in value])


def qcolor_to_color4f(value: QColor) -> Color4f:
    return value.redF(), value.greenF(), value.blueF(), value.alphaF()


def color_to_color4f(value: Color, alpha: bool = True) -> Color4f:
    r, g, b, a = value.as_rgb_tuple(alpha=True)  # type: ignore[misc]
    return round(r / 255, 4), round(g / 255, 4), round(b / 255, 4), a if alpha else 1.0


def id_to_color(obj_id: int) -> Color4f:
    # Supports up to 256³ = 16,777,216 objects
    r = ((obj_id >> 16) & 0xFF) / 255.0
    g = ((obj_id >> 8) & 0xFF) / 255.0
    b = (obj_id & 0xFF) / 255.0
    return (round(r, 4), round(g, 4), round(b, 4), 1.0)


def color_to_id(r: int, g: int, b: int) -> int:
    return b | (g << 8) | (r << 16)


def compute_face_normals(vertices: np.ndarray) -> np.ndarray:
    normals: list[float] = []
    for i in range(0, len(vertices), 9):
        normal = Vector3D(*vertices[i : i + 3]).normal(
            Vector3D(*vertices[i + 3 : i + 6]),
            Vector3D(*vertices[i + 6 : i + 9]),
        )
        normals.extend([normal.x, normal.y, normal.z] * 3)
    return np.array(normals, dtype=np.float32)


def compute_smooth_normals(vertices: np.ndarray, tolerance: float = 1e-6) -> np.ndarray:
    """
    Compute smooth vertex normals by averaging face normals of adjacent triangles.
    Vertices within tolerance distance are considered the same vertex.
    """
    # Reshape vertices to (num_vertices, 3) for vectorized operations
    vertices_reshaped = vertices.reshape(-1, 3)
    num_triangles = len(vertices_reshaped) // 3

    # Compute all face normals at once using vectorized operations
    v1 = vertices_reshaped[0::3]
    v2 = vertices_reshaped[1::3]
    v3 = vertices_reshaped[2::3]

    # Cross product to get face normals
    edge1 = v2 - v1
    edge2 = v3 - v1
    face_normals = np.cross(edge1, edge2)

    # Normalize face normals
    norms = np.linalg.norm(face_normals, axis=1, keepdims=True)
    face_normals = np.divide(face_normals, norms, where=norms != 0)

    # Round vertices for grouping
    decimals = max(0, -int(np.log10(tolerance)))
    rounded_vertices = np.round(vertices_reshaped, decimals)

    # Build mapping from unique vertices to their indices
    unique_vertices, inverse_indices = np.unique(rounded_vertices, axis=0, return_inverse=True)

    # Accumulate normals for each unique vertex
    accumulated_normals = np.zeros((len(unique_vertices), 3), dtype=np.float32)
    for tri_idx in range(num_triangles):
        face_normal = face_normals[tri_idx]
        for local_idx in range(3):
            vertex_idx = tri_idx * 3 + local_idx
            unique_idx = inverse_indices[vertex_idx]
            accumulated_normals[unique_idx] += face_normal

    # Normalize accumulated normals
    norms = np.linalg.norm(accumulated_normals, axis=1, keepdims=True)
    accumulated_normals = np.divide(accumulated_normals, norms, where=norms != 0)

    # Map back to original vertex order
    normals = accumulated_normals[inverse_indices]

    return normals.reshape(-1).astype(np.float32)


def unwind_vertices(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    vertices_reshaped = vertices.reshape(-1, 3)
    return vertices_reshaped[faces].reshape(-1).astype(np.float32)


def reverse_winding_order(vertices: np.ndarray) -> np.ndarray:
    """
    Reverse the winding order of triangles by swapping vertex positions.
    This changes triangle orientation from clockwise to counter-clockwise or vice versa.
    """
    vertices_reshaped = vertices.reshape(-1, 9)
    # Swap second and third vertex of each triangle
    vertices_reshaped[:, [3, 4, 5, 6, 7, 8]] = vertices_reshaped[:, [6, 7, 8, 3, 4, 5]]
    return vertices_reshaped.reshape(-1).astype(np.float32)


def crop_image_to_content(image: np.ndarray, bg_color: tuple[float, ...]) -> np.ndarray:
    xmin = ymin = xmax = ymax = -1
    color = [round(c * 255) for c in bg_color]

    mask = np.any(image != color, axis=-1)
    rows_with_content = np.any(mask, axis=1)
    if np.any(rows_with_content):
        ymin = np.argmax(rows_with_content)  # type: ignore[assignment]

    cols_with_content = np.any(mask, axis=0)
    if np.any(rows_with_content):
        ymax = len(rows_with_content) - 1 - np.argmax(rows_with_content[::-1])  # type: ignore[assignment]

    if np.any(cols_with_content):
        xmin = np.argmax(cols_with_content)  # type: ignore[assignment]

    if np.any(cols_with_content):
        xmax = len(cols_with_content) - 1 - np.argmax(cols_with_content[::-1])  # type: ignore[assignment]

    if xmin >= 0 and xmax >= 0 and ymin >= 0 and ymax >= 0:
        left, top, width, height = xmin, ymin, xmax - xmin + 1, ymax - ymin + 1
        image = image[top : top + height, left : left + width]

    return image
