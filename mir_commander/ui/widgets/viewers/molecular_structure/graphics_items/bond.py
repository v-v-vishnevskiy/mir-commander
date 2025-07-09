from PySide6.QtGui import QQuaternion, QVector3D

from mir_commander.ui.utils.opengl.graphics_items import Item, MeshItem
from mir_commander.ui.utils.opengl.mesh import Cylinder
from mir_commander.ui.utils.opengl.utils import Color4f

from .atom import Atom


class BondItem(MeshItem):
    def __init__(
        self,
        mesh_data: Cylinder,
        position: QVector3D,
        direction: QVector3D,
        radius: float,
        length: float,
        color: Color4f,
    ):
        super().__init__(mesh_data, color=color)
        self._position = position
        self._direction = direction
        self._radius = radius
        self._length = length

        self._compute_transform()

    def _compute_transform(self):
        self._transform.setToIdentity()
        self._transform.translate(self._position)
        self._transform.rotate(QQuaternion.rotationTo(QVector3D(0.0, 0.0, -1.0), self._direction))
        self._transform.scale(self._radius, self._radius, self._length)

    @property
    def visible(self) -> bool:
        return super().visible and self.parent.visible

    def set_transformation(self, position: QVector3D, direction: QVector3D, radius: float, length: float):
        self._position = position
        self._direction = direction
        self._radius = radius
        self._length = length
        self._compute_transform()

    def set_radius(self, radius: float):
        self._radius = radius
        self._compute_transform()


class Bond(Item):
    def __init__(
        self,
        c_mesh_data: Cylinder,
        atom_1: Atom,
        atom_2: Atom,
        radius: float = 0.1,
        atoms_color: bool = True,
        color: Color4f = (0.5, 0.5, 0.5, 1.0),
    ):
        super().__init__(is_container=True, picking_visible=False)

        self._c_mesh_data = c_mesh_data
        self._radius = radius
        self._atom_1 = atom_1
        self._atom_2 = atom_2
        self._smooth = True
        self._atoms_color = atoms_color
        self._color = color
        self._items: list[BondItem] = []

        self._add_bonds()

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
            self.add_child(BondItem(self._c_mesh_data, position, direction, self._radius, length, color))

    def update_bonds(self):
        bonds = self._build_bonds()
        direction = self._atom_1.position - self._atom_2.position
        for i, bond in enumerate(self.children):
            position, length, color = bonds[i]
            bond.set_transformation(position, direction, self._radius, length)
            bond.set_color(color)

    @property
    def visible(self) -> bool:
        return super().visible and not self._atom_1.cloaked and not self._atom_2.cloaked

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

    def set_smooth(self, smooth: bool):
        self._smooth = smooth
        for item in self.children:
            item.set_smooth(smooth)

    def __repr__(self) -> str:
        return f"Bond(id={self._id}, atom_1={self._atom_1}, atom_2={self._atom_2})"
