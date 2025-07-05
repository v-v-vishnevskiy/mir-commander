import math

import numpy as np
from PySide6.QtGui import QVector3D

from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.utils.opengl.graphics_items.item import Item
from mir_commander.ui.utils.opengl.mesh import Cylinder, Sphere
from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.utils import Color4f, normalize_color
from mir_commander.utils.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.utils.chem import atomic_number_to_symbol

from .config import MolecularStructureViewerConfig
from .graphics_items.atom import Atom
from .graphics_items.bond import Bond
from .shaders import OUTLINE
from .style import Style


class Molecule(Item):
    def __init__(self, config: MolecularStructureViewerConfig):
        super().__init__()

        self._config = config
        self._style = Style(config)
        self.center = QVector3D(0, 0, 0)
        self._atom_mesh_data = Sphere(stacks=Sphere.min_stacks, slices=Sphere.min_slices, radius=1.0)
        self._bond_mesh_data = Cylinder(stacks=1, slices=Cylinder.min_slices, radius=1.0, length=1.0, caps=False)
        self._edge_shader = ShaderProgram(VertexShader(OUTLINE["vertex"]), FragmentShader(OUTLINE["fragment"]))
        self._atom_index_under_cursor: None | Atom = None
        self._current_geom_bond_tol = self._config.geom_bond_tol

        self.atom_items: list[Atom] = []
        self.bond_items: list[Bond] = []
        self.selected_atom_items: list[Atom] = []

        self.apply_style()

    def update(self):
        print("update")

    def paint_self(self):
        pass

    def build(self, atomic_coordinates: AtomicCoordinates):
        """
        Builds molecule graphics object from `AtomicCoordinates` data structure
        """

        longest_distance = 0

        # add atoms
        for i, atomic_num in enumerate(atomic_coordinates.atomic_num):
            position = QVector3D(atomic_coordinates.x[i], atomic_coordinates.y[i], atomic_coordinates.z[i])
            atom = self.add_atom(i, atomic_num, position)

            d = position.length() + atom.radius
            if longest_distance < d:
                longest_distance = d

        # add bonds
        self.build_bonds(atomic_coordinates, self._current_geom_bond_tol)

        self.center = QVector3D(
            x=np.sum(atomic_coordinates.x) / len(atomic_coordinates.x), 
            y=np.sum(atomic_coordinates.y) / len(atomic_coordinates.y), 
            z=np.sum(atomic_coordinates.z) / len(atomic_coordinates.z),
        )

    def apply_style(self):
        mesh_quality = self._style.current.quality.mesh
        self._apply_atoms_style(mesh_quality)
        self._apply_bonds_style(mesh_quality)

        self.update()

    def set_style(self, name: str):
        self._style.set_style(name)
        self.apply_style()

    def set_next_style(self):
        if self._style.set_next_style():
            self.apply_style()

    def set_prev_style(self):
        if self._style.set_prev_style():
            self.apply_style()

    def _apply_atoms_style(self, mesh_quality: int):
        # update mesh
        s_stacks, s_slices = Sphere.min_stacks * mesh_quality, Sphere.min_slices * mesh_quality
        if (s_stacks, s_slices) != (self._atom_mesh_data.stacks, self._atom_mesh_data.slices):
            self._atom_mesh_data.generate_mesh(stacks=s_stacks, slices=s_slices, radius=self._atom_mesh_data.radius)
            self._atom_mesh_data.compute_vertex_normals()
            self._atom_mesh_data.compute_face_normals()

        # update items
        for atom in self.atom_items:
            radius, color = self._get_atom_radius_and_color(atom.atomic_num)
            atom.set_radius(radius)
            atom.set_color(color)
            atom.set_smooth(self._style.current.quality.smooth)
    
    def _get_atom_radius_and_color(self, atomic_num: int) -> tuple[float, Color4f]:
        atoms_radius = self._style.current.atoms.radius
        if atoms_radius == "atomic":
            if atomic_num >= 0:
                radius = self._style.current.atoms.atomic_radius[atomic_num]
            else:
                radius = self._style.current.atoms.special_atoms.atomic_radius[atomic_num]
            radius *= self._style.current.atoms.scale_factor
        elif atoms_radius == "bond":
            radius = self._style.current.bond.radius
        else:
            raise ValueError(f"Invalid atoms.radius '{atoms_radius}' in style '{self._style.current.name}'")

        if atomic_num >= 0:
            color = self._style.current.atoms.atomic_color[atomic_num]
        else:
            color = self._style.current.atoms.special_atoms.atomic_color[atomic_num]

        return radius, normalize_color(color)

    def _apply_bonds_style(self, mesh_quality: int):
        # update mesh
        c_slices = Cylinder.min_slices * mesh_quality
        if c_slices != self._bond_mesh_data.slices:
            self._bond_mesh_data.generate_mesh(
                stacks=self._bond_mesh_data.stacks,
                slices=c_slices,
                radius=self._bond_mesh_data.radius,
                length=self._bond_mesh_data.length,
                caps=self._bond_mesh_data.caps,
            )
            self._bond_mesh_data.compute_vertex_normals()
            self._bond_mesh_data.compute_face_normals()

        # update items
        for bond in self.bond_items:
            bond.set_radius(self._style.current.bond.radius)

            if self._style.current.bond.color == "atoms":
                bond.set_atoms_color(True)
            else:
                bond.set_color(normalize_color(self._style.current.bond.color))

            bond.set_smooth(self._style.current.quality.smooth)

    def clear(self):
        self.atom_items.clear()
        self.bond_items.clear()
        super().clear()

    def build_bonds(self, ds: AtomicCoordinates, geom_bond_tol: float):
        for i in range(len(ds.atomic_num)):
            if ds.atomic_num[i] < 1:
                continue
            crad_i = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[i]]
            for j in range(i):
                if ds.atomic_num[j] < 1:
                    continue
                crad_j = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[j]]
                crad_sum = crad_i + crad_j
                dist_ij = math.sqrt((ds.x[i] - ds.x[j]) ** 2 + (ds.y[i] - ds.y[j]) ** 2 + (ds.z[i] - ds.z[j]) ** 2)
                if dist_ij < (crad_sum + crad_sum * geom_bond_tol):
                    self.add_bond(self.atom(i), self.atom(j))

    def add_atom(self, index_num: int, atomic_num: int, position: QVector3D) -> Atom:
        radius, color = self._get_atom_radius_and_color(atomic_num)

        item = Atom(
            self._atom_mesh_data,
            index_num,
            atomic_num,
            atomic_number_to_symbol(atomic_num),
            position,
            radius,
            color,
            selected_shader=self._edge_shader,
        )
        item.set_smooth(self._style.current.quality.smooth)
        self.add_child(item)
        self.atom_items.append(item)

        return item

    def add_bond(self, atom_1: Atom, atom_2: Atom) -> Bond:
        atoms_color = self._style.current.bond.color == "atoms"
        if atoms_color:
            color = (0.5, 0.5, 0.5, 1.0)
        else:
            color = normalize_color(self._style.current.bond.color)

        item = Bond(
            self._bond_mesh_data,
            atom_1,
            atom_2,
            self._style.current.bond.radius,
            atoms_color,
            color,
        )
        item.set_smooth(self._style.current.quality.smooth)
        self.add_child(item)
        self.bond_items.append(item)

        return item

    def remove_bond(self, index: int):
        self.remove_child(self.bond_items[index])
        self.bond_items.pop(index)

    def remove_bond_all(self):
        for bond in self.bond_items:
            self.remove_child(bond)
        self.bond_items.clear()

    def atom(self, index: int) -> Atom:
        return self.atom_items[index]

    def bond_index(self, atom1: Atom, atom2: Atom) -> int:
        """
        Check the list of bonds if there exists a bond between atoms atom1 and atom2.
        Return the index of the bond in the list or -1 if no bond has been found.
        """
        for idx, bond in enumerate(self.bond_items):
            if (bond._atom_1 == atom1 and bond._atom_2 == atom2) or (bond._atom_1 == atom2 and bond._atom_2 == atom1):
                return idx
        return -1

    def select_all_atoms(self):
        for atom in self.atom_items:
            atom.selected = True
        self.update()
        self.selected_atom_items = self.atom_items.copy()

    def unselect_all_atoms(self):
        for atom in self.atom_items:
            atom.selected = False
        self.update()
        self.selected_atom_items = []

    def select_toggle_all_atoms(self):
        """
        Unselect all atoms if at least one atom selected,
        otherwise select all.
        """
        if len(self.selected_atom_items) > 0:
            self.unselect_all_atoms()
        else:
            self.select_all_atoms()

    def toggle_atom_selection(self, x: int, y: int):
        atom = self._atom_under_cursor(x, y)
        if atom is not None:
            if atom.toggle_selection():
                self.selected_atom_items.append(atom)
            else:
                self.selected_atom_items.remove(atom)
            self.update()

    def highlight_atom_under_cursor(self, x: int, y: int):
        atom = self._atom_under_cursor(x, y)
        if atom:
            if atom != self._atom_index_under_cursor:
                if self._atom_index_under_cursor is not None:
                    self._atom_index_under_cursor.set_under_cursor(False)
                atom.set_under_cursor(True)
                self.update()
                self.short_msg_signal.emit(f"{atom.element_symbol}{atom.index_num + 1}")
        elif self._atom_index_under_cursor:
            self._atom_index_under_cursor.set_under_cursor(False)
            self.update()
        self._atom_index_under_cursor = atom

    def _atom_under_cursor(self, x: int, y: int) -> None | Atom:
        if not self.atom_items:
            return None

        result = None
        point, direction = self.point_to_line(x, y)
        direction.normalize()
        distance = None
        for atom in self.atom_items:
            if atom.cross_with_line_test(point, direction):
                d = atom.position.distanceToPoint(point)
                if distance is None or d < distance:
                    result = atom
                    distance = d
        return result

    def cloak_selected_atoms(self):
        for atom in self.atom_items:
            if atom.selected:
                atom.cloaked = True
        self.update()

    def cloak_not_selected_atoms(self):
        for atom in self.atom_items:
            if not atom.selected:
                atom.cloaked = True
        self.update()

    def cloak_h_atoms(self):
        for atom in self.atom_items:
            if atom.atomic_num == 1:
                atom.cloaked = True
        self.update()

    def cloak_not_selected_h_atoms(self):
        for atom in self.atom_items:
            if atom.atomic_num == 1 and not atom.selected:
                atom.cloaked = True
        self.update()

    def cloak_atoms_by_atnum(self, atomic_num: int):
        for atom in self.atom_items:
            if atom.atomic_num == atomic_num:
                atom.cloaked = True
        self.update()

    def cloak_toggle_h_atoms(self):
        for atom in self.atom_items:
            if atom.atomic_num == 1:
                atom.cloaked = not atom.cloaked
        self.update()

    def uncloak_all_atoms(self):
        for atom in self.atom_items:
            atom.cloaked = False
        self.update()
