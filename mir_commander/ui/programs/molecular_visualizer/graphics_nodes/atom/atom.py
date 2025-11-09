from time import monotonic
from typing import TYPE_CHECKING

from PySide6.QtGui import QVector3D

from mir_commander.ui.sdk.opengl.scene import Node, NodeType
from mir_commander.ui.sdk.opengl.utils import Color4f
from mir_commander.utils.chem import atomic_number_to_symbol

from ...config import AtomLabelConfig, SelectedAtom
from .bounding_sphere import BoundingSphere
from .label import Label
from .sphere import Sphere

if TYPE_CHECKING:
    from ..bond import Bond


class Atom(Node):
    def __init__(
        self,
        index_number: int,
        atomic_number: int,
        position: QVector3D,
        radius: float,
        color: Color4f,
        selected_atom_config: SelectedAtom,
        label_config: AtomLabelConfig,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs | dict(node_type=NodeType.CONTAINER))

        self.set_position(position)

        self._index = index_number
        self.atomic_num = atomic_number
        self._related_bonds: set["Bond"] = set()
        self._cloaked = False  # if `True` do not draw this atom and its bonds.
        self._selected = False
        self._selected_atom_config = selected_atom_config
        self._label_config = label_config
        self._sphere = Sphere(radius, color, parent=self)
        self._bounding_sphere: None | BoundingSphere = None
        self._label = Label(self._label_config, self.element_symbol, self._index + 1, parent=self)
        self._selection_update = 0.0

        self._update_label_position()

    def add_related_bond(self, bond: "Bond"):
        self._related_bonds.add(bond)

    def set_cloaked(self, value: bool):
        self._cloaked = value
        self.set_visible(not self._cloaked)
        for bond in self._related_bonds:
            atom_1, atom_2 = bond.atoms
            bond.set_visible(atom_1.visible and atom_2.visible)

    @property
    def index(self) -> int:
        return self._index

    @property
    def element_symbol(self) -> str:
        return atomic_number_to_symbol(self.atomic_num)

    @property
    def position(self) -> QVector3D:
        return self._transform._position

    @property
    def color(self) -> Color4f:
        return self._sphere.color

    @property
    def cloaked(self) -> bool:
        return self._cloaked

    @property
    def radius(self) -> float:
        return self._sphere.radius

    @property
    def related_bonds(self) -> set["Bond"]:
        return self._related_bonds

    @property
    def selected(self) -> bool:
        return self._selected

    @property
    def selection_update(self) -> float:
        return self._selection_update

    @property
    def bounding_sphere(self) -> BoundingSphere:
        if self._bounding_sphere is None:
            self._bounding_sphere = BoundingSphere(self._selected_atom_config, parent=self._sphere)
        return self._bounding_sphere

    @property
    def label(self) -> Label:
        return self._label

    def _update_label_position(self):
        self._label.set_position(QVector3D(0.0, 0.0, self._sphere.radius * self._label_config.offset))

    def remove(self):
        self.remove_all_bonds()
        super().remove()

    def remove_all_bonds(self):
        while len(self._related_bonds) > 0:
            self._related_bonds.pop().remove()

    def remove_bond(self, bond: "Bond"):
        self._related_bonds.discard(bond)

    def set_index_number(self, value: int):
        if value == self._index:
            return

        self._index = value
        self._label.set_number(value + 1)

    def set_atomic_number(self, value: int):
        if self.atomic_num == value:
            return

        self.atomic_num = value

        self._label.set_symbol(atomic_number_to_symbol(value))

    def set_color(self, color: Color4f):
        self._sphere.set_color(color)

    def set_radius(self, radius: float):
        self._sphere.set_radius(radius)
        self._update_label_position()

    def set_selected(self, value: bool):
        self._selection_update = monotonic()
        self._selected = value
        self.bounding_sphere.set_visible(value)

    def toggle_selection(self) -> bool:
        self._selection_update = monotonic()
        self.set_selected(not self._selected)
        return self._selected

    def set_label_visible(self, value: bool):
        self.label.set_visible(value)

    def set_symbol_visible(self, value: bool):
        self.label.set_symbol_visible(value)

    def set_number_visible(self, value: bool):
        self.label.set_number_visible(value)

    def set_selected_atom_config(self, config: SelectedAtom):
        self.bounding_sphere.set_config(config)

    def set_label_config(self, config: AtomLabelConfig):
        self.label.set_config(config)

    def set_label_size(self, size: int):
        self.label.set_size(size)

    def set_label_offset(self, offset: float):
        self._label_config.offset = offset
        self.label.set_position(QVector3D(0.0, 0.0, self.radius * offset))

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"symbol={self.element_symbol}, "
            f"index={self._index + 1}, "
            f"selected={self.selected}, "
            f"cloaked={self.cloaked}"
            ")"
        )
