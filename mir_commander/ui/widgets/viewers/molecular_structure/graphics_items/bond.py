from PySide6.QtGui import QQuaternion, QVector3D

from mir_commander.ui.utils.opengl.resource_manager import SceneNode
from mir_commander.ui.utils.opengl.utils import Color4f

from .atom import Atom


class BondItem(SceneNode):
    def __init__(
        self,
        resource_name: str,
        position: QVector3D,
        direction: QVector3D,
        radius: float,
        length: float,
        color: Color4f,
    ):
        super().__init__(picking_visible=False)
        self.set_mesh(resource_name)
        self.set_vbo(resource_name)
        self.set_color(color)
        self.set_shader("default")
        self.set_transformation(position, direction, radius, length)

    def set_transformation(self, position: QVector3D, direction: QVector3D, radius: float, length: float):
        self.translate(position)
        self.set_rotation(QQuaternion.rotationTo(QVector3D(0.0, 0.0, -1.0), direction))
        self.set_scale(QVector3D(radius, radius, length))


class Bond(SceneNode):
    def __init__(
        self,
        resource_name: str,
        atom_1: Atom,
        atom_2: Atom,
        radius: float = 0.1,
        atoms_color: bool = True,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
    ):
        super().__init__(is_container=True, picking_visible=False)

        self._resource_name = resource_name
        self._radius = radius
        self._atom_1 = atom_1
        self._atom_2 = atom_2
        self._smooth = True
        self._atoms_color = atoms_color
        self._color = color
        self._items: list[BondItem] = []

        atom_1.add_related_bond(self)
        atom_2.add_related_bond(self)

        self._add_bonds()

    @property
    def atoms(self) -> tuple[Atom, Atom]:
        return self._atom_1, self._atom_2

    def _build_bonds(self) -> list[tuple[QVector3D, float, Color4f]]:
        result = []

        length = (self._atom_1.position - self._atom_2.position).length()
        if self._atoms_color and self._atom_1.atomic_num != self._atom_2.atomic_num:
            mid_length = length - self._atom_1.radius - self._atom_2.radius
            if mid_length > 0:
                length_1 = self._atom_1.radius + mid_length / 2
                length_2 = self._atom_2.radius + mid_length / 2
                mid = self._atom_2.position - self._atom_1.position
                mid.normalize()
                mid = (mid * length_1) + self._atom_1.position
                result.append((self._atom_1.position, length_1, self._atom_1.color))
                result.append((mid, length_2, self._atom_2.color))
        else:
            position = self._atom_1.position
            result.append((position, length, self._atom_1.color if self._atoms_color else self._color))

        return result

    def _add_bonds(self):
        self.clear()
        bonds = self._build_bonds()
        direction = self._atom_1.position - self._atom_2.position
        for position, length, color in bonds:
            self.add_node(BondItem(self._resource_name, position, direction, self._radius, length, color))

    def update_bonds(self):
        bonds = self._build_bonds()
        direction = self._atom_1.position - self._atom_2.position
        for i, bond in enumerate(self._nodes):
            position, length, color = bonds[i]
            bond.set_transformation(position, direction, self._radius, length)
            bond.set_color(color)

    def set_radius(self, radius: float):
        self._radius = radius
        for bond in self._nodes:
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
            for bond in self._nodes:
                bond.set_color(color)

    def __repr__(self) -> str:
        return f"Bond(id={self._id}, atom_1={self._atom_1}, atom_2={self._atom_2})"
