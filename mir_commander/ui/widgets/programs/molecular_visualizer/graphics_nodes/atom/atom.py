from time import monotonic
from typing import TYPE_CHECKING

from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f

from ...config import AtomLabelConfig, AtomLabelType, SelectedAtom
from .bounding_sphere import BoundingSphere
from .label import Label
from .sphere import Sphere

if TYPE_CHECKING:
    from ..bond import Bond


class Atom(Node):
    def __init__(
        self,
        index_num: int,
        atomic_num: int,
        element_symbol: str,
        position: QVector3D,
        radius: float,
        color: Color4f,
        selected_atom_config: SelectedAtom,
        label_config: AtomLabelConfig,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs | dict(node_type=NodeType.CONTAINER))

        self.translate(position)

        self.index_num = index_num
        self.atomic_num = atomic_num
        self.element_symbol = element_symbol
        self._related_bonds: list["Bond"] = []
        self._cloaked = False  # if `True` do not draw this atom and its bonds.
        self._selected = False
        self._selected_atom_config = selected_atom_config
        self._label_config = label_config
        self._sphere = Sphere(radius, color, parent=self)
        self._bounding_sphere: None | BoundingSphere = None
        self._label: None | Label = None
        self._selection_update = 0.0

    def add_related_bond(self, bond: "Bond"):
        self._related_bonds.append(bond)

    def set_cloaked(self, value: bool):
        self._cloaked = value
        self.set_visible(not self._cloaked)
        for bond in self._related_bonds:
            atom_1, atom_2 = bond.atoms
            bond.set_visible(atom_1.visible and atom_2.visible)

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
        if self._label is None:
            self._label = Label(self._label_config, parent=self)
            self._label.set_position(QVector3D(0.0, 0.0, self._sphere.radius * self._label_config.offset))
            self.set_label_type(self._label_config.type)
        return self._label

    def set_color(self, color: Color4f):
        self._sphere.set_color(color)

    def set_radius(self, radius: float):
        self._sphere.set_radius(radius)

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

    def set_label_type(self, value: AtomLabelType):
        if value == AtomLabelType.INDEX_NUMBER:
            self.label.set_text(f"{self.index_num + 1}")
        elif value == AtomLabelType.ELEMENT_SYMBOL:
            self.label.set_text(f"{self.element_symbol}")
        elif value == AtomLabelType.ELEMENT_SYMBOL_AND_INDEX_NUMBER:
            self.label.set_text(f"{self.element_symbol}{self.index_num + 1}")

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
            f"element_symbol={self.element_symbol}, "
            f"index_num={self.index_num + 1}, "
            f"selected={self.selected}, "
            f"cloaked={self.cloaked}"
            ")"
        )
