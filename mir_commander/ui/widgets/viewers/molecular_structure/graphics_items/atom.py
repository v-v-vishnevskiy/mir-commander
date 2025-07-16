from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.resource_manager import SceneNode
from mir_commander.ui.utils.opengl.utils import Color4f

from ..config import SelectedAtom
from .bounding_sphere import BoundingSphere


class Atom(SceneNode):
    def __init__(
        self,
        resource_name: str,
        index_num: int,
        atomic_num: int,
        element_symbol: str,
        position: QVector3D,
        radius: float,
        color: Color4f,
        selected_atom_config: SelectedAtom,
    ):
        super().__init__(picking_visible=True)
        self.translate(position)
        self.set_scale(radius)
        self.set_color(color)
        self.set_mesh(resource_name)
        self.set_vao(resource_name)
        self.set_shader("default")

        self._radius = radius
        self.index_num = index_num
        self.atomic_num = atomic_num
        self.element_symbol = element_symbol
        self._related_bonds = []
        self._cloaked = False  # if `True` do not draw this atom and its bonds.
        self._selected = False
        self._bounding_sphere = BoundingSphere(resource_name, color, selected_atom_config)
        self.add_node(self._bounding_sphere)

    def add_related_bond(self, bond: SceneNode):
        self._related_bonds.append(bond)

    def set_cloaked(self, value: bool):
        self._cloaked = value
        for bond in self._related_bonds:
            atom_1, atom_2 = bond.atoms
            bond.set_visible(bool((not atom_1.cloaked) * (not atom_2.cloaked)))
        self.invalidate_root_node()

    @property
    def position(self) -> QVector3D:
        return self._transform._translation

    @property
    def cloaked(self) -> bool:
        return self._cloaked

    @property
    def visible(self) -> bool:
        return super().visible and not self._cloaked

    def set_under_cursor(self, value: bool):
        if value:
            radius = self.radius * 1.15
        else:
            radius = self.radius
        self.set_scale(radius)

    @property
    def radius(self) -> float:
        return self._radius

    def set_radius(self, radius: float):
        self._radius = radius
        self.set_scale(radius)

    def set_selected_atom_config(self, config: SelectedAtom):
        self._bounding_sphere.set_config(config)

    @property
    def selected(self) -> bool:
        return self._selected

    def set_selected(self, value: bool):
        self._selected = value
        self.invalidate_root_node()

    def toggle_selection(self) -> bool:
        self.set_selected(not self._selected)
        return self._selected

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, index_num={self.index_num + 1}, element_symbol={self.element_symbol})"
