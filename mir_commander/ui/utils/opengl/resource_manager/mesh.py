import numpy as np

from .base import Resource


class Mesh(Resource):
    __slots__ = ("vertices", "normals")

    def __init__(self, name: str, vertices: np.ndarray, normals: np.ndarray):
        super().__init__(name)
        self.vertices: np.ndarray = vertices
        self.normals: np.ndarray = normals

    def __repr__(self):
        return f"Mesh(name={self.name}, vertices={len(self.vertices)}, normals={len(self.normals)})"
