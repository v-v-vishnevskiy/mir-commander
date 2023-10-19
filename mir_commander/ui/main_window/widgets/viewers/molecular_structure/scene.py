from PySide6.QtGui import QVector3D
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from mir_commander.ui.main_window.widgets.viewers.molecular_structure.graphics_items import Atom, Bond
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.style import Style
from mir_commander.ui.utils.opengl.mesh import Cylinder, Hemisphere, Sphere
from mir_commander.ui.utils.opengl.scene import Scene as BaseScene
from mir_commander.ui.utils.opengl.utils import Color4f


class Scene(BaseScene):
    def __init__(self, widget: QOpenGLWidget, style: Style):
        super().__init__(widget)

        self.__atom_mesh_data = Sphere(rows=Sphere.min_rows, cols=Sphere.min_cols, radius=1.0)
        self.__bond_mesh_data = Cylinder(rows=1, cols=Cylinder.min_cols, radius=1.0, length=1.0, caps=False)
        self.__bond_cap_mesh_data = Hemisphere(rows=Hemisphere.min_rows, cols=Hemisphere.min_cols, radius=1.0)

        self.__atom_items: list[Atom] = []
        self.__bond_items: list[Bond] = []

        self.__atom_index_under_cursor: None | Atom = None

        self.style = style

    def __apply_atoms_style(self, mesh_quality: int):
        # update mesh
        s_rows, s_cols = Sphere.min_rows * mesh_quality, Sphere.min_cols * mesh_quality
        if (s_rows, s_cols) != (self.__atom_mesh_data.rows, self.__atom_mesh_data.cols):
            self.__atom_mesh_data.generate_mesh(rows=s_rows, cols=s_cols, radius=self.__atom_mesh_data.radius)
            self.__atom_mesh_data.compute_vertex_normals()
            self.__atom_mesh_data.compute_face_normals()

        # update items
        for atom in self.__atom_items:
            atom.enabled = self.style["atoms.enabled"]
            if self.style["atoms.enabled"]:
                atom.set_radius(self.style["atoms.scale_factor"] * self.style["atoms.radius"][atom.atomic_num])

            atom.set_color(self.normalize_color(self.style["atoms.color"][atom.atomic_num]))

            atom.set_smooth(self.style["quality.smooth"])

    def __apply_bonds_style(self, mesh_quality: int):
        # update mesh
        c_cols = Cylinder.min_cols * mesh_quality
        if c_cols != self.__bond_mesh_data.cols:
            self.__bond_mesh_data.generate_mesh(
                rows=self.__bond_mesh_data.rows,
                cols=c_cols,
                radius=self.__bond_mesh_data.radius,
                length=self.__bond_mesh_data.length,
                caps=self.__bond_mesh_data.caps,
            )
            self.__bond_mesh_data.compute_vertex_normals()
            self.__bond_mesh_data.compute_face_normals()

        h_rows, h_cols = Hemisphere.min_rows * mesh_quality, Hemisphere.min_cols * mesh_quality
        if (h_rows, h_cols) != (self.__bond_cap_mesh_data.rows, self.__bond_cap_mesh_data.cols):
            self.__bond_cap_mesh_data.generate_mesh(
                rows=h_rows,
                cols=h_cols,
                radius=self.__bond_cap_mesh_data.radius,
            )
            self.__bond_cap_mesh_data.compute_vertex_normals()
            self.__bond_cap_mesh_data.compute_face_normals()

        # update items
        for bond in self.__bond_items:
            bond.set_radius(self.style["bond.radius"])

            if self.style["bond.color"] == "atoms":
                bond.set_atoms_color(True)
            else:
                bond.set_color(self.normalize_color(self.style["bond.color"]))

            bond.set_smooth(self.style["quality.smooth"])

    def _atom_under_cursor(self, x: int, y: int) -> None | Atom:
        if not self.__atom_items:
            return None

        result = None
        point, direction = self.point_to_line(x, y)
        direction.normalize()
        distance = None
        for atom in self.__atom_items:
            if atom.cross_with_line_test(point, direction):
                d = atom.position.distanceToPoint(point)
                if distance is None or d < distance:
                    result = atom
                    distance = d
        return result

    def _highlight_atom_under_cursor(self, x: int, y: int):
        if not self.__atom_items:
            return

        atom = self._atom_under_cursor(x, y)
        if atom:
            if atom != self.__atom_index_under_cursor:
                if self.__atom_index_under_cursor is not None:
                    self.__atom_index_under_cursor.set_under_cursor(False)
                atom.set_under_cursor(True)
                self.update()
        elif self.__atom_index_under_cursor:
            self.__atom_index_under_cursor.set_under_cursor(False)
            self.update()
        self.__atom_index_under_cursor = atom

    def initialize_gl(self):
        super().initialize_gl()
        self.apply_style()

    def apply_style(self):
        mesh_quality = self.style["quality.mesh"]
        mesh_quality = max(min(mesh_quality, 100), 1)
        self.__apply_atoms_style(mesh_quality)
        self.__apply_bonds_style(mesh_quality)

        self.set_background_color(self.normalize_color(self.style["background.color"]))

        self.set_projection_mode(self.style["projection.mode"])
        self.set_fov(self.style["projection.fov"])

        self.update()

    def clear(self):
        self.__atom_items.clear()
        self.__bond_items.clear()
        super().clear()

    def add_atom(self, atomic_num: int, position: QVector3D) -> Atom:
        if self.style["atoms.enabled"]:
            radius = self.style["atoms.scale_factor"] * self.style["atoms.radius"][atomic_num]
        else:
            radius = self.style["bond.radius"]

        color = self.normalize_color(self.style["atoms.color"][atomic_num])

        item = Atom(self.__atom_mesh_data, atomic_num, position, radius, color)
        item.enabled = self.style["atoms.enabled"]
        item.set_smooth(self.style["quality.smooth"])
        self.add_item(item)

        self.__atom_items.append(item)

        return item

    def add_bond(self, atom_1: Atom, atom_2: Atom) -> Bond:
        atoms_color = self.style["bond.color"] == "atoms"
        if atoms_color:
            color = (0.5, 0.5, 0.5, 1.0)
        else:
            color = self.normalize_color(self.style["bond.color"])

        item = Bond(
            self.__bond_mesh_data,
            self.__bond_cap_mesh_data,
            atom_1,
            atom_2,
            self.style["bond.radius"],
            atoms_color,
            color,
        )
        item.set_smooth(self.style["quality.smooth"])
        self.add_item(item)

        self.__bond_items.append(item)

        return item

    def atom(self, index: int) -> Atom:
        return self.__atom_items[index]

    def set_style(self, name: str):
        self.style.set_style(name)
        self.apply_style()

    def normalize_color(self, value: str) -> Color4f:
        """
        Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
        """
        return int(value[1:3], 16) / 255, int(value[3:5], 16) / 255, int(value[5:7], 16) / 255, 1.0

    def move_cursor(self, x: int, y: int):
        self._highlight_atom_under_cursor(x, y)
