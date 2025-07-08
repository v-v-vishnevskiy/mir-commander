from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.graphics_items import MeshItem
from mir_commander.ui.utils.opengl.enums import PaintMode
from mir_commander.ui.utils.opengl.mesh import Sphere
from mir_commander.ui.utils.opengl.shader import ShaderProgram
from mir_commander.ui.utils.opengl.utils import Color4f

from ..config import SelectedAtom
from .bounding_sphere import BoundingSphere


class Atom(MeshItem):
    def __init__(
        self,
        mesh_data: Sphere,
        index_num: int,
        atomic_num: int,
        element_symbol: str,
        position: QVector3D,
        radius: float,
        color: Color4f,
        selected_shader: ShaderProgram,
        selected_atom_config: SelectedAtom,
    ):
        super().__init__(mesh_data, color=color)
        self.position = position
        self.radius = radius
        self.index_num = index_num
        self.atomic_num = atomic_num
        self.element_symbol = element_symbol
        self.cloaked = False  # if `True` do not draw this atom and its bonds. Also see `Bond.paint` method
        self._selected = False
        self._under_cursor = False
        self._compute_transform()
        self._bounding_sphere = BoundingSphere(mesh_data, radius, selected_shader, color, selected_atom_config)
        self.add_child(self._bounding_sphere)

    def _compute_transform(self):
        self._transform.setToIdentity()
        self._transform.translate(self.position)

        radius = self.radius
        if self._under_cursor:
            radius *= 1.15

        self._transform.scale(radius, radius, radius)

    def paint_self(self, mode: PaintMode):
        if not self.cloaked:
            super().paint_self(mode)

    def set_under_cursor(self, value: bool):
        if self._under_cursor != value:
            self._under_cursor = value
            self._compute_transform()

    def set_radius(self, radius: float):
        self.radius = radius
        self._compute_transform()

    def set_position(self, position: QVector3D):
        self.position = position
        self._compute_transform()

    def set_selected_atom_config(self, config: SelectedAtom):
        self._bounding_sphere.set_config(config)

    @property
    def selected(self) -> bool:
        return self._selected

    def set_selected(self, value: bool):
        self._selected = value
        self._bounding_sphere.visible = value

    def toggle_selection(self) -> bool:
        self._selected = not self._selected
        self._bounding_sphere.visible = not self._bounding_sphere.visible
        return self._selected

    def __repr__(self) -> str:
        return f"Atom(id={self._id}, atomic_num={self.atomic_num}, element_symbol={self.element_symbol})"
