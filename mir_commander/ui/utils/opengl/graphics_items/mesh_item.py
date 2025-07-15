from mir_commander.ui.utils.opengl.mesh_object import MeshObject
from mir_commander.ui.utils.opengl.utils import Color4f

from .item import Item


class MeshItem(Item):
    def __init__(
        self,
        mesh_object: MeshObject,
        smooth: bool = True,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
    ):
        super().__init__()
        self._mesh_object = mesh_object
        self._mesh_data = mesh_object.mesh_data
        self._vao = mesh_object.vao
        self._smooth = smooth
        self._color = color
        self._mesh_id = mesh_object.id

    @property
    def mesh_id(self) -> int:
        return self._mesh_id

    @property
    def color(self) -> Color4f:
        return self._color

    def set_color(self, color: Color4f):
        self._color = color
