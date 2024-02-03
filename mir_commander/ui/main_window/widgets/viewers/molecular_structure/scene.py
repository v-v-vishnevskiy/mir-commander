from PySide6.QtGui import QVector3D
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from mir_commander.ui.main_window.widgets.viewers.molecular_structure.graphics_items import Atom, Bond
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.shaders import OUTLINE
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.style import Style
from mir_commander.ui.utils.opengl.mesh import Cylinder, Sphere
from mir_commander.ui.utils.opengl.scene import Scene as BaseScene
from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.utils import Color4f
from mir_commander.utils.chem import atomic_number_to_symbol


class Scene(BaseScene):
    def __init__(self, widget: QOpenGLWidget, style: Style):
        super().__init__(widget)

        self._atom_mesh_data = Sphere(stacks=Sphere.min_stacks, slices=Sphere.min_slices, radius=1.0)
        self._bond_mesh_data = Cylinder(stacks=1, slices=Cylinder.min_slices, radius=1.0, length=1.0, caps=False)

        self.atom_items: list[Atom] = []
        self.selected_atom_items: list[Atom] = []
        self.bond_items: list[Bond] = []
        self._edge_shader = ShaderProgram(VertexShader(OUTLINE["vertex"]), FragmentShader(OUTLINE["fragment"]))

        self._atom_index_under_cursor: None | Atom = None

        self.style = style

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
            atom.set_smooth(self.style["quality.smooth"])

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
            bond.set_radius(self.style["bond.radius"])

            if self.style["bond.color"] == "atoms":
                bond.set_atoms_color(True)
            else:
                bond.set_color(self.normalize_color(self.style["bond.color"]))

            bond.set_smooth(self.style["quality.smooth"])

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

    def _get_atom_radius_and_color(self, atomic_num: int) -> tuple[float, Color4f]:
        atoms_radius = self.style["atoms.radius"]
        if atoms_radius == "atomic":
            if atomic_num >= 0:
                radius = self.style["atoms.atomic_radius"][atomic_num]
            else:
                radius = self.style["atoms.special_atoms.atomic_radius"][atomic_num]
            radius *= self.style["atoms.scale_factor"]
        elif atoms_radius == "bond":
            radius = self.style["bond.radius"]
        else:
            raise ValueError(f"Invalid atoms.radius '{atoms_radius}' in style '{self.style['name']}'")

        if atomic_num >= 0:
            color = self.style["atoms.atomic_color"][atomic_num]
        else:
            color = self.style["atoms.special_atoms.atomic_color"][atomic_num]

        return radius, self.normalize_color(color)

    def _highlight_atom_under_cursor(self, x: int, y: int):
        atom = self._atom_under_cursor(x, y)
        if atom:
            if atom != self._atom_index_under_cursor:
                if self._atom_index_under_cursor is not None:
                    self._atom_index_under_cursor.set_under_cursor(False)
                atom.set_under_cursor(True)
                self.update()
                self._gl_widget._main_window.status.showMessage(f"{atom.element_symbol}{atom.index_num+1}", 10000)
        elif self._atom_index_under_cursor:
            self._atom_index_under_cursor.set_under_cursor(False)
            self.update()
        self._atom_index_under_cursor = atom

    def toggle_atom_selection(self):
        atom = self._atom_under_cursor(*self.mouse_pos)
        if atom is not None:
            if atom.toggle_selection():
                self.selected_atom_items.append(atom)
            else:
                self.selected_atom_items.remove(atom)
            self.update()

    def initialize_gl(self):
        super().initialize_gl()
        self.apply_style()

    def apply_style(self):
        mesh_quality = self.style["quality.mesh"]
        mesh_quality = max(min(mesh_quality, 100), 1)
        self._apply_atoms_style(mesh_quality)
        self._apply_bonds_style(mesh_quality)

        self.set_background_color(self.normalize_color(self.style["background.color"]))

        self.set_projection_mode(self.style["projection.mode"])
        self.set_fov(self.style["projection.fov"])

        self.update()

    def clear(self, update: bool = True):
        self.atom_items.clear()
        self.bond_items.clear()
        super().clear(update)

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
        item.set_smooth(self.style["quality.smooth"])
        self.add_item(item)

        self.atom_items.append(item)

        return item

    def add_bond(self, atom_1: Atom, atom_2: Atom) -> Bond:
        atoms_color = self.style["bond.color"] == "atoms"
        if atoms_color:
            color = (0.5, 0.5, 0.5, 1.0)
        else:
            color = self.normalize_color(self.style["bond.color"])

        item = Bond(
            self._bond_mesh_data,
            atom_1,
            atom_2,
            self.style["bond.radius"],
            atoms_color,
            color,
        )
        item.set_smooth(self.style["quality.smooth"])
        self.add_item(item)

        self.bond_items.append(item)

        return item

    def remove_bond(self, idx: int):
        self.remove_item(self.bond_items[idx])
        self.bond_items.pop(idx)

    def remove_bond_all(self):
        for bond in self.bond_items:
            self.remove_item(bond)
        self.bond_items.clear()

    def atom(self, index: int) -> Atom:
        return self.atom_items[index]

    def bond_idx(self, atom1: Atom, atom2: Atom) -> int:
        """
        Check the list of bonds if there exists a bond between atoms atom1 and atom2.
        Return the index of the bond in the list or -1 if no bond has been found.
        """
        for idx, bond in enumerate(self.bond_items):
            if (bond._atom_1 == atom1 and bond._atom_2 == atom2) or (bond._atom_1 == atom2 and bond._atom_2 == atom1):
                return idx
        return -1

    def set_style(self, name: str):
        self.style.set_style(name)
        self.apply_style()

    def normalize_color(self, value: str) -> Color4f:
        """
        Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
        """
        return int(value[1:3], 16) / 255, int(value[3:5], 16) / 255, int(value[5:7], 16) / 255, 1.0

    def new_cursor_position(self, x: int, y: int):
        self._highlight_atom_under_cursor(x, y)

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
