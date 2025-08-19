import numpy as np

from .base import Resource


class Mesh(Resource):
    __slots__ = ("vertices", "normals", "tex_coords")

    def __init__(self, name: str, vertices: np.ndarray, normals: np.ndarray, tex_coords: None | np.ndarray = None):
        super().__init__(name)
        self.vertices: np.ndarray = vertices
        self.normals: np.ndarray = normals
        self.tex_coords: None | np.ndarray = tex_coords

    def __repr__(self):
        return (
            f"Mesh("
            f"name={self.name}, "
            f"vertices={len(self.vertices) // 3}, "
            f"normals={len(self.normals) // 3}, "
            f"tex_coords={len(self.tex_coords) // 2 if self.tex_coords is not None else None}"
            ")"
        )
