from mir_commander.core.algebra import Vector3D
from mir_commander.core.graphics.scene.node import Node, NodeType
from mir_commander.core.graphics.utils import Color4f

from .atom.atom import Atom
from .cylinder import Cylinder


class Bond(Node):
    def __init__(
        self,
        atom_1: Atom,
        atom_2: Atom,
        radius: float = 0.1,
        atoms_color: bool = True,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs | dict(node_type=NodeType.CONTAINER, visible=True))

        self._radius = radius
        self._atom_1 = atom_1
        self._atom_2 = atom_2
        self._smooth = True
        self._atoms_color = atoms_color
        self._color = color

        atom_1.add_related_bond(self)
        atom_2.add_related_bond(self)

        self._add_bonds()

    @property
    def atoms(self) -> tuple[Atom, Atom]:
        return self._atom_1, self._atom_2

    def remove(self):
        self._atom_1.remove_bond(self)
        self._atom_2.remove_bond(self)
        super().remove()

    def _build_bonds(self) -> list[tuple[Vector3D, Vector3D, float, Color4f]]:
        direction = (self._atom_2.position - self._atom_1.position).normalized
        length = (self._atom_1.position - self._atom_2.position).length
        if self._atoms_color and self._atom_1.atomic_num != self._atom_2.atomic_num:
            mid_length = (length - self._atom_1.radius - self._atom_2.radius) / 2
            if mid_length > 0:
                length_1 = self._atom_1.radius + mid_length
                length_2 = self._atom_2.radius + mid_length
                return [
                    (self._atom_1.position, direction, length_1, self._atom_1.color),
                    (self._atom_1.position + direction * length_1, direction, length_2, self._atom_2.color),
                ]
        else:
            return [
                (self._atom_1.position, direction, length, self._atom_1.color if self._atoms_color else self._color)
            ]
        return []

    def _add_bonds(self):
        self.clear()
        bonds = self._build_bonds()
        for position, direction, length, color in bonds:
            c = Cylinder(direction, parent=self, node_type=NodeType.OPAQUE)
            c.set_color(color)
            c.set_size(self._radius, length)
            c.set_position(position)

    def set_radius(self, radius: float):
        self._radius = radius
        for bond in self.children:
            bond.set_radius(radius)

    def set_atoms_color(self, value: bool):
        if self._atoms_color != value:
            self._atoms_color = value
            self._add_bonds()

    def set_color(self, color: Color4f):
        self._color = color
        if self._atoms_color:
            self._atoms_color = False
            self._add_bonds()
        else:
            for bond in self.children:
                bond.set_color(color)

    def __repr__(self) -> str:
        return f"Bond(atom_1={self._atom_1}, atom_2={self._atom_2})"
