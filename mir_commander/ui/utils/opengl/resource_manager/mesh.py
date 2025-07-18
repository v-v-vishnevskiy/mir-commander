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
        return f"Mesh(name={self.name}, vertices={len(self.vertices)}, normals={len(self.normals)}, tex_coords={len(self.tex_coords)})"
