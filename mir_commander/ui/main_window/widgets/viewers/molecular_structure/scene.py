from PySide6.QtGui import QVector3D
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from mir_commander.ui.main_window.widgets.viewers.molecular_structure.graphics_items import Atom, Bond
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.shaders import OUTLINE
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.style import Style
from mir_commander.ui.utils.opengl.mesh import Cylinder, Sphere
from mir_commander.ui.utils.opengl.scene import Scene as BaseScene
from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.utils import Color4f


class Scene(BaseScene):
    def __init__(self, widget: QOpenGLWidget, style: Style):
        super().__init__(widget)

        self._atom_mesh_data = Sphere(stacks=Sphere.min_stacks, slices=Sphere.min_slices, radius=1.0)
        self._bond_mesh_data = Cylinder(stacks=1, slices=Cylinder.min_slices, radius=1.0, length=1.0, caps=False)

        self._atom_items: list[Atom] = []
        self._bond_items: list[Bond] = []
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
        for atom in self._atom_items:
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
        for bond in self._bond_items:
            bond.set_radius(self.style["bond.radius"])

            if self.style["bond.color"] == "atoms":
                bond.set_atoms_color(True)
            else:
                bond.set_color(self.normalize_color(self.style["bond.color"]))

            bond.set_smooth(self.style["quality.smooth"])

    def _atom_under_cursor(self, x: int, y: int) -> None | Atom:
        if not self._atom_items:
            return None

        result = None
        point, direction = self.point_to_line(x, y)
        direction.normalize()
        distance = None
        for atom in self._atom_items:
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
        elif self._atom_index_under_cursor:
            self._atom_index_under_cursor.set_under_cursor(False)
            self.update()
        self._atom_index_under_cursor = atom

    def toggle_atom_selection(self):
        atom = self._atom_under_cursor(*self.mouse_pos)
        if atom is not None:
            atom.toggle_selection()
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
        self._atom_items.clear()
        self._bond_items.clear()
        super().clear(update)

    def add_atom(self, atomic_num: int, position: QVector3D) -> Atom:
        radius, color = self._get_atom_radius_and_color(atomic_num)
        item = Atom(self._atom_mesh_data, atomic_num, position, radius, color, selected_shader=self._edge_shader)
        item.set_smooth(self.style["quality.smooth"])
        self.add_item(item)

        self._atom_items.append(item)

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

        self._bond_items.append(item)

        return item

    def atom(self, index: int) -> Atom:
        return self._atom_items[index]

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
