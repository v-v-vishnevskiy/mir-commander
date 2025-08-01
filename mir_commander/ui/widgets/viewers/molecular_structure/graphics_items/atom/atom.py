from PySide6.QtGui import QVector3D

from mir_commander.ui.utils.opengl.scene import BaseNode, ContainerNode
from mir_commander.ui.utils.opengl.utils import Color4f

from ...config import AtomLabelConfig, AtomLabelType, SelectedAtom
from .bounding_sphere import BoundingSphere
from .label import Label
from .sphere import Sphere


class Atom(ContainerNode):
    def __init__(
        self,
        parent: BaseNode,
        model_name: str,
        index_num: int,
        atomic_num: int,
        element_symbol: str,
        position: QVector3D,
        radius: float,
        color: Color4f,
        selected_atom_config: SelectedAtom,
        label_config: AtomLabelConfig,
    ):
        super().__init__(parent=parent, visible=True)
        self.translate(position)

        self.index_num = index_num
        self.atomic_num = atomic_num
        self.element_symbol = element_symbol
        self._related_bonds = []
        self._cloaked = False  # if `True` do not draw this atom and its bonds.
        self._selected = False
        self._sphere = Sphere(self, model_name, radius, color)
        self._bounding_sphere = BoundingSphere(self._sphere, model_name, color, selected_atom_config)
        self._label = Label(self, label_config)
        self._label.set_translation(QVector3D(0.0, 0.0, radius * 1.01))
        self.set_label_type(label_config.type)

    def add_related_bond(self, bond: BaseNode):
        self._related_bonds.append(bond)

    def set_cloaked(self, value: bool):
        self._cloaked = value
        self.set_visible(not self._cloaked)
        for bond in self._related_bonds:
            atom_1, atom_2 = bond.atoms
            bond.set_visible(atom_1.visible and atom_2.visible)

    @property
    def position(self) -> QVector3D:
        return self._transform._translation

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

    def highlight(self, value: bool):
        r = self._sphere.highlight(value)
        self._label.set_translation(QVector3D(0.0, 0.0, r * 1.01))

    def set_radius(self, radius: float):
        self._sphere.set_radius(radius)

    def set_selected(self, value: bool):
        self._selected = value
        self._bounding_sphere.set_visible(value)

    def toggle_selection(self) -> bool:
        self.set_selected(not self._selected)
        return self._selected

    def set_label_visible(self, value: bool):
        self._label.set_visible(value)

    def set_label_type(self, value: AtomLabelType):
        if value == AtomLabelType.INDEX_NUMBER:
            self._label.set_text(f"{self.index_num + 1}")
        elif value == AtomLabelType.ELEMENT_SYMBOL:
            self._label.set_text(f"{self.element_symbol}")
        elif value == AtomLabelType.ELEMENT_SYMBOL_AND_INDEX_NUMBER:
            self._label.set_text(f"{self.element_symbol}{self.index_num + 1}")

    def set_selected_atom_config(self, config: SelectedAtom):
        self._bounding_sphere.set_config(config)

    def set_label_config(self, config: AtomLabelConfig):
        self._label.set_config(config)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"element_symbol={self.element_symbol}, "
            f"index_num={self.index_num + 1}, "
            f"selected={self.selected}, "
            f"cloaked={self.cloaked}"
            ")"
        )
