import math
from itertools import combinations
from typing import Optional

import numpy as np
import OpenGL.error
from pydantic_extra_types.color import Color
from PySide6.QtCore import Slot
from PySide6.QtGui import QStandardItem, QVector3D
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget

from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.utils.opengl.keymap import Keymap
from mir_commander.ui.utils.opengl.mesh import Cylinder, Sphere
from mir_commander.ui.utils.opengl.opengl_widget import OpenGLWidget
from mir_commander.ui.utils.opengl.shader import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.utils import Color4f
from mir_commander.ui.utils.widget import TR
from mir_commander.utils.chem import atomic_number_to_symbol, symbol_to_atomic_number
from mir_commander.utils.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.utils.math import geom_angle_xyz, geom_distance_xyz, geom_oop_angle_xyz, geom_torsion_angle_xyz

from ..base import BaseViewer

from .build_bonds_dialog import BuildBondsDialog
from .config import MolecularStructureViewerConfig
from .graphics_items import Atom, Bond
from .save_image_dialog import SaveImageDialog
from .shaders import OUTLINE
from .style import Style


class InteratomicDistance:
    def __init__(self, atom1: Atom, atom2: Atom):
        self.atom1 = atom1
        self.atom2 = atom2
        self.value = 0.0


class InteratomicAngle:
    def __init__(self, atom1: Atom, atom2: Atom, atom3: Atom):
        self.atom1 = atom1
        self.atom2 = atom2
        self.atom3 = atom3
        self.value = 0.0


class InteratomicTorsion:
    def __init__(self, atom1: Atom, atom2: Atom, atom3: Atom, atom4: Atom):
        self.atom1 = atom1
        self.atom2 = atom2
        self.atom3 = atom3
        self.atom4 = atom4
        self.value = 0.0


class InteratomicOutOfPlane:
    def __init__(self, atom1: Atom, atom2: Atom, atom3: Atom, atom4: Atom):
        self.atom1 = atom1
        self.atom2 = atom2
        self.atom3 = atom3
        self.atom4 = atom4
        self.value = 0.0


class MolecularStructureViewer(OpenGLWidget, BaseViewer):
    def __init__(self, parent: QWidget, config: MolecularStructureViewerConfig, item: QStandardItem, all: bool = False):
        super().__init__(
            parent=parent, 
            keymap=Keymap(config.keymap.viewer.model_dump()), 
            antialiasing=config.antialiasing,
        )
        self._config = config
        self._style = Style(config)

        self._atom_mesh_data = Sphere(stacks=Sphere.min_stacks, slices=Sphere.min_slices, radius=1.0)
        self._bond_mesh_data = Cylinder(stacks=1, slices=Cylinder.min_slices, radius=1.0, length=1.0, caps=False)
        self.atom_items: list[Atom] = []
        self.bond_items: list[Bond] = []
        self.selected_atom_items: list[Atom] = []
        self._edge_shader = ShaderProgram(VertexShader(OUTLINE["vertex"]), FragmentShader(OUTLINE["fragment"]))

        self._atom_index_under_cursor: None | Atom = None

        self.item = item
        self._all = all
        self._current_geom_bond_tol = self._config.geom_bond_tol

        self.setMinimumSize(self._config.min_size[0], self._config.min_size[1])
        self.resize(self._config.size[0], self._config.size[1])

        self._molecule_index = 0
        self._draw_item = None
        self._set_draw_item()

        self.action_handler.add_action("toggle_atom_selection", False, self.toggle_atom_selection)

        self.update_window_title()

        self.apply_style()

        self._build_molecule()

    def clear(self, update: bool = True):
        self.atom_items.clear()
        self.bond_items.clear()
        super().clear(update)

    def apply_style(self):
        mesh_quality = self._style.current.quality.mesh
        self._apply_atoms_style(mesh_quality)
        self._apply_bonds_style(mesh_quality)

        self.set_background_color(self.normalize_color(self._style.current.background.color))

        self.set_projection_mode(self._style.current.projection.mode)
        self.set_perspective_projection_fov(self._style.current.projection.perspective.fov)

        self.update()

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
                bond.set_color(self.normalize_color(self._style.current.bond.color))

            bond.set_smooth(self._style.current.quality.smooth)

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
        self.scene.add_item(item)

        self.atom_items.append(item)

        return item

    def add_bond(self, atom_1: Atom, atom_2: Atom) -> Bond:
        atoms_color = self._style.current.bond.color == "atoms"
        if atoms_color:
            color = (0.5, 0.5, 0.5, 1.0)
        else:
            color = self.normalize_color(self._style.current.bond.color)

        item = Bond(
            self._bond_mesh_data,
            atom_1,
            atom_2,
            self._style.current.bond.radius,
            atoms_color,
            color,
        )
        item.set_smooth(self._style.current.quality.smooth)
        self.scene.add_item(item)

        self.bond_items.append(item)

        return item

    def remove_bond(self, index: int):
        self.scene.remove_item(self.bond_items[index])
        self.bond_items.pop(index)

    def remove_bond_all(self):
        for bond in self.bond_items:
            self.scene.remove_item(bond)
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

    def set_style(self, name: str):
        self._style.current.set_style(name)
        self.apply_style()

    def normalize_color(self, value: Color) -> Color4f:
        """
        Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
        """

        r, g, b = value.as_rgb_tuple()
        return r / 255, g / 255, b / 255, 1.0

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

    def _atomic_coordinates_item(
        self, index: int, parent: QStandardItem, counter: int = -1
    ) -> tuple[bool, int, Optional[QStandardItem]]:
        """
        Finds item with `AtomicCoordinates` data structure
        """
        index = max(0, index)
        last_item = None
        if not parent.hasChildren() and isinstance(parent.data().data, AtomicCoordinates):
            return True, 0, parent
        else:
            for i in range(parent.rowCount()):
                item = parent.child(i)
                if isinstance(item.data().data, AtomicCoordinates):
                    last_item = item
                    counter += 1
                    if index == counter:
                        return True, counter, item
                elif self._all and item.hasChildren():
                    found, counter, item = self._atomic_coordinates_item(index, item, counter)
                    last_item = item
                    if found:
                        return found, counter, item
            return False, counter, last_item

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

        return radius, self.normalize_color(color)

    def _highlight_atom_under_cursor(self, x: int, y: int):
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

    def toggle_atom_selection(self):
        atom = self._atom_under_cursor(*self.cursor_position)
        if atom is not None:
            if atom.toggle_selection():
                self.selected_atom_items.append(atom)
            else:
                self.selected_atom_items.remove(atom)
            self.update()

    def _build_molecule(self):
        """
        Builds molecule graphics object from `AtomicCoordinates` data structure
        """
        if not self._draw_item:
            return None

        ds: AtomicCoordinates = self._draw_item.data().data

        longest_distance = 0

        # add atoms
        for i, atomic_num in enumerate(ds.atomic_num):
            position = QVector3D(ds.x[i], ds.y[i], ds.z[i])
            atom = self.add_atom(i, atomic_num, position)

            d = position.length() + atom.radius
            if longest_distance < d:
                longest_distance = d

        # add bonds
        self._build_bonds(ds, self._current_geom_bond_tol)

        center = QVector3D(np.sum(ds.x) / len(ds.x), np.sum(ds.y) / len(ds.y), np.sum(ds.z) / len(ds.z))
        self.set_scene_translate(-center)
        self.set_scene_translate(QVector3D(0, 0, (-longest_distance - center.length()) * 3.6))

    def _build_bonds(self, ds: AtomicCoordinates, geom_bond_tol: float):
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

    def _set_draw_item(self):
        _, self._molecule_index, self._draw_item = self._atomic_coordinates_item(self._molecule_index, self.item)

    def set_prev_style(self):
        if self._style.set_prev_style():
            self.apply_style()

    def set_next_style(self):
        if self._style.set_next_style():
            self.apply_style()

    def set_prev_atomic_coordinates(self):
        if self._molecule_index > 0:
            self._molecule_index -= 1
            self._set_draw_item()
            self.update_window_title()
            self.clear(update=False)
            self._build_molecule()
            self.update()

    def set_next_atomic_coordinates(self):
        self._molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if id(item) != id(self._draw_item):
            self.update_window_title()
            self.clear(update=False)
            self._build_molecule()
            self.update()

    # TODO: uncomment when context menu is implemented
    # def contextMenuEvent(self, event: QContextMenuEvent):
    #    # Show the context menu
    #    self.context_menu.exec(event.globalPos())

    def update_window_title(self):
        title = self._draw_item.text()
        parent_item = self._draw_item.parent()
        while parent_item:
            title = parent_item.text() + "/" + title
            parent_item = parent_item.parent()
        self.setWindowTitle(title)
        self.setWindowIcon(self._draw_item.icon())

    @Slot()
    def save_img_action_handler(self):
        dlg = SaveImageDialog(self.size().width(), self.size().height(), self._draw_item.text(), self)
        if dlg.exec():
            save_flag = True
            if dlg.img_file_path.exists():
                ret = QMessageBox.warning(
                    self,
                    self.tr("Save image"),
                    self.tr("The file already exists:")
                    + f"\n{dlg.img_file_path}\n"
                    + self.tr("Do you want to overwrite it?"),
                    QMessageBox.Yes | QMessageBox.No,
                )
                if ret != QMessageBox.Yes:
                    save_flag = False

            if save_flag:
                image = None
                try:
                    image = self.render_to_image(
                        dlg.img_width, dlg.img_height, dlg.transparent_bg, dlg.crop_to_content
                    )
                except OpenGL.error.GLError as error:
                    message_box = QMessageBox(
                        QMessageBox.Critical,
                        self.tr("Error image rendering"),
                        self.tr("OpenGL cannot create image."),
                        QMessageBox.Close,
                    )
                    message_box.setDetailedText(str(error))
                    message_box.exec()

                if image is not None:
                    if image.save(str(dlg.img_file_path)):
                        self.short_msg_signal.emit(TR.tr("Image saved"))
                    else:
                        QMessageBox.critical(
                            self,
                            self.tr("Save image"),
                            self.tr("Could not save image:")
                            + f"\n{dlg.img_file_path}\n"
                            + self.tr("The path does not exist or is write-protected."),
                        )

    def cloak_atoms_by_atnum(self):
        el_symbol, ok = QInputDialog.getText(
            self, self.tr("Cloak atoms by type"), self.tr("Enter element symbol:"), QLineEdit.Normal, ""
        )
        if ok:
            try:
                self.cloak_atoms_by_atnum(symbol_to_atomic_number(el_symbol))
            except ValueError:
                QMessageBox.critical(
                    self,
                    self.tr("Cloak atoms by type"),
                    self.tr("Invalid element symbol!"),
                    buttons=QMessageBox.StandardButton.Ok,
                )

    def calc_distance_last2sel_atoms(self):
        """
        Calculate and print distance (in internal units) between last two selected atoms.
        """
        if len(self.selected_atom_items) >= 2:
            atom1 = self.selected_atom_items[-2]
            atom2 = self.selected_atom_items[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            distance = geom_distance_xyz(pos1.x(), pos1.y(), pos1.z(), pos2.x(), pos2.y(), pos2.z())
            self.long_msg_signal.emit(
                f"r({atom1.element_symbol}{atom1.index_num+1}-{atom2.element_symbol}{atom2.index_num+1})={distance:.3f}"
            )
        else:
            QMessageBox.critical(
                self,
                self.tr("Interatomic distance"),
                self.tr("At least two atoms must be selected!"),
                buttons=QMessageBox.StandardButton.Ok,
            )

    def calc_angle_last3sel_atoms(self):
        """
        Calculate and print angle (in degrees) formed by last three selected atoms: a1-a2-a3
        """
        if len(self.selected_atom_items) >= 3:
            atom1 = self.selected_atom_items[-3]
            atom2 = self.selected_atom_items[-2]
            atom3 = self.selected_atom_items[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            pos3 = atom3.position
            angle = geom_angle_xyz(
                pos1.x(), pos1.y(), pos1.z(), pos2.x(), pos2.y(), pos2.z(), pos3.x(), pos3.y(), pos3.z()
            ) * (180.0 / math.pi)
            self.long_msg_signal.emit(
                f"a({atom1.element_symbol}{atom1.index_num+1}-{atom2.element_symbol}{atom2.index_num+1}-"
                f"{atom3.element_symbol}{atom3.index_num+1})={angle:.1f}"
            )
        else:
            QMessageBox.critical(
                self,
                self.tr("Angle"),
                self.tr("At least three atoms must be selected!"),
                buttons=QMessageBox.StandardButton.Ok,
            )

    def calc_torsion_last4sel_atoms(self):
        """
        Calculate and print torsion angle (in degrees) formed by last four selected atoms: a1-a2-a3-a4
        """
        if len(self.selected_atom_items) >= 4:
            atom1 = self.selected_atom_items[-4]
            atom2 = self.selected_atom_items[-3]
            atom3 = self.selected_atom_items[-2]
            atom4 = self.selected_atom_items[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            pos3 = atom3.position
            pos4 = atom4.position
            angle = geom_torsion_angle_xyz(
                pos1.x(),
                pos1.y(),
                pos1.z(),
                pos2.x(),
                pos2.y(),
                pos2.z(),
                pos3.x(),
                pos3.y(),
                pos3.z(),
                pos4.x(),
                pos4.y(),
                pos4.z(),
            ) * (180.0 / math.pi)
            self.long_msg_signal.emit(
                f"t({atom1.element_symbol}{atom1.index_num+1}-{atom2.element_symbol}{atom2.index_num+1}-"
                f"{atom3.element_symbol}{atom3.index_num+1}-{atom4.element_symbol}{atom4.index_num+1})={angle:.1f}"
            )
        else:
            QMessageBox.critical(
                self,
                self.tr("Torsion angle"),
                self.tr("At least four atoms must be selected!"),
                buttons=QMessageBox.StandardButton.Ok,
            )

    def calc_oop_last4sel_atoms(self):
        """
        Calculate and print out-of-plane angle (in degrees) formed by last four selected atoms: a1-a2-a3-a4
        """
        if len(self.selected_atom_items) >= 4:
            atom1 = self.selected_atom_items[-4]
            atom2 = self.selected_atom_items[-3]
            atom3 = self.selected_atom_items[-2]
            atom4 = self.selected_atom_items[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            pos3 = atom3.position
            pos4 = atom4.position
            angle = geom_oop_angle_xyz(
                pos1.x(),
                pos1.y(),
                pos1.z(),
                pos2.x(),
                pos2.y(),
                pos2.z(),
                pos3.x(),
                pos3.y(),
                pos3.z(),
                pos4.x(),
                pos4.y(),
                pos4.z(),
            ) * (180.0 / math.pi)
            self.long_msg_signal.emit(
                f"o({atom1.element_symbol}{atom1.index_num+1}-{atom2.element_symbol}{atom2.index_num+1}<"
                f"{atom3.element_symbol}{atom3.index_num+1}/{atom4.element_symbol}{atom4.index_num+1})={angle:.1f}"
            )
        else:
            QMessageBox.critical(
                self,
                self.tr("Out-of-plane angle"),
                self.tr("At least four atoms must be selected!"),
                buttons=QMessageBox.StandardButton.Ok,
            )

    def calc_auto_lastsel_atoms(self):
        """
        Calculate and print internal geometrical parameter,
        distance, angle or torsion angle, depending on the number of selected atoms.
        """
        num_selected = len(self.selected_atom_items)
        if num_selected == 2:
            self.calc_distance_last2sel_atoms()
        elif num_selected == 3:
            self.calc_angle_last3sel_atoms()
        elif num_selected == 4:
            self.calc_torsion_last4sel_atoms()
        else:
            QMessageBox.critical(
                self,
                self.tr("Auto geometrical parameter"),
                self.tr("Two, three or four atoms must be selected!"),
                buttons=QMessageBox.StandardButton.Ok,
            )

    def calc_all_parameters_selected_atoms(self):
        """
        Calculate and print all parameters formed by all selected atoms
        """
        distances = []
        angles = []
        torsions = []
        outofplanes = []

        # Generate list of distances, which are bonds formed by selected atoms
        for bond in self.bond_items:
            if bond._atom_1.selected and bond._atom_2.selected:
                distances.append(InteratomicDistance(bond._atom_1, bond._atom_2))

        # Calculate distances
        for dist in distances:
            dist.value = geom_distance_xyz(
                dist.atom1.position.x(),
                dist.atom1.position.y(),
                dist.atom1.position.z(),
                dist.atom2.position.x(),
                dist.atom2.position.y(),
                dist.atom2.position.z(),
            )

        # Generate list of angles
        n = len(distances)
        for i in range(n):
            for j in range(i + 1, n):
                if distances[i].atom1 == distances[j].atom1:
                    angles.append(InteratomicAngle(distances[i].atom2, distances[i].atom1, distances[j].atom2))
                elif distances[i].atom2 == distances[j].atom1:
                    angles.append(InteratomicAngle(distances[i].atom1, distances[i].atom2, distances[j].atom2))
                elif distances[i].atom1 == distances[j].atom2:
                    angles.append(InteratomicAngle(distances[i].atom2, distances[i].atom1, distances[j].atom1))
                elif distances[i].atom2 == distances[j].atom2:
                    angles.append(InteratomicAngle(distances[i].atom1, distances[i].atom2, distances[j].atom1))

        # Calculate angles
        for angle in angles:
            angle.value = geom_angle_xyz(
                angle.atom1.position.x(),
                angle.atom1.position.y(),
                angle.atom1.position.z(),
                angle.atom2.position.x(),
                angle.atom2.position.y(),
                angle.atom2.position.z(),
                angle.atom3.position.x(),
                angle.atom3.position.y(),
                angle.atom3.position.z(),
            ) * (180.0 / math.pi)

        # Generate list of torsions
        ndist = len(distances)
        nang = len(angles)
        for i in range(nang):
            if angles[i].value >= 175.0:
                continue
            for j in range(ndist):
                # If the bond is already a part of the angle
                if (
                    distances[j].atom1 == angles[i].atom1
                    or distances[j].atom1 == angles[i].atom2
                    or distances[j].atom1 == angles[i].atom3
                ) and (
                    distances[j].atom2 == angles[i].atom1
                    or distances[j].atom2 == angles[i].atom2
                    or distances[j].atom2 == angles[i].atom3
                ):
                    continue

                torsion = None
                if angles[i].atom1 == distances[j].atom1:
                    torsion = InteratomicTorsion(distances[j].atom2, angles[i].atom1, angles[i].atom2, angles[i].atom3)
                elif angles[i].atom1 == distances[j].atom2:
                    torsion = InteratomicTorsion(distances[j].atom1, angles[i].atom1, angles[i].atom2, angles[i].atom3)
                elif angles[i].atom3 == distances[j].atom1:
                    torsion = InteratomicTorsion(angles[i].atom1, angles[i].atom2, angles[i].atom3, distances[j].atom2)
                elif angles[i].atom3 == distances[j].atom2:
                    torsion = InteratomicTorsion(angles[i].atom1, angles[i].atom2, angles[i].atom3, distances[j].atom1)

                if torsion:
                    # Check if this (or equivalent) torsion is already in the list
                    exists = False
                    for etors in torsions:
                        if (
                            etors.atom1 == torsion.atom1
                            and etors.atom2 == torsion.atom2
                            and etors.atom3 == torsion.atom3
                            and etors.atom4 == torsion.atom4
                        ) or (
                            etors.atom1 == torsion.atom4
                            and etors.atom2 == torsion.atom3
                            and etors.atom3 == torsion.atom2
                            and etors.atom4 == torsion.atom1
                        ):
                            exists = True
                            break

                    if not exists:
                        torsions.append(torsion)

        # Calculate torsions
        for torsion in torsions:
            torsion.value = geom_torsion_angle_xyz(
                torsion.atom1.position.x(),
                torsion.atom1.position.y(),
                torsion.atom1.position.z(),
                torsion.atom2.position.x(),
                torsion.atom2.position.y(),
                torsion.atom2.position.z(),
                torsion.atom3.position.x(),
                torsion.atom3.position.y(),
                torsion.atom3.position.z(),
                torsion.atom4.position.x(),
                torsion.atom4.position.y(),
                torsion.atom4.position.z(),
            ) * (180.0 / math.pi)

        # Generate list of out-of-plane angles
        for i in range(nang):
            if angles[i].value >= 175.0:
                continue
            for j in range(ndist):
                # If the bond is already a part of the angle
                if (
                    distances[j].atom1 == angles[i].atom1
                    or distances[j].atom1 == angles[i].atom2
                    or distances[j].atom1 == angles[i].atom3
                ) and (
                    distances[j].atom2 == angles[i].atom1
                    or distances[j].atom2 == angles[i].atom2
                    or distances[j].atom2 == angles[i].atom3
                ):
                    continue

                outofplane = None
                # If the bond is connected to the central (2nd) atom of the angle
                if angles[i].atom2 == distances[j].atom1:
                    outofplane = InteratomicOutOfPlane(
                        distances[j].atom2, angles[i].atom2, angles[i].atom1, angles[i].atom3
                    )
                elif angles[i].atom2 == distances[j].atom2:
                    outofplane = InteratomicOutOfPlane(
                        distances[j].atom1, angles[i].atom2, angles[i].atom1, angles[i].atom3
                    )

                if outofplane:
                    # Check if the first atom is terminal
                    terminal = False
                    # Iterate by bonds
                    for k in range(ndist):
                        if k != j and (
                            distances[k].atom1 == outofplane.atom1 or distances[k].atom2 == outofplane.atom1
                        ):
                            terminal = True
                            break

                    if not terminal:
                        outofplanes.append(outofplane)

        # Calculate out-of-planes
        for outofplane in outofplanes:
            outofplane.value = geom_oop_angle_xyz(
                outofplane.atom1.position.x(),
                outofplane.atom1.position.y(),
                outofplane.atom1.position.z(),
                outofplane.atom2.position.x(),
                outofplane.atom2.position.y(),
                outofplane.atom2.position.z(),
                outofplane.atom3.position.x(),
                outofplane.atom3.position.y(),
                outofplane.atom3.position.z(),
                outofplane.atom4.position.x(),
                outofplane.atom4.position.y(),
                outofplane.atom4.position.z(),
            ) * (180.0 / math.pi)

        # Print parameters
        out_str = ""
        for dist in distances:
            out_str += (
                f"r({dist.atom1.element_symbol}{dist.atom1.index_num+1}-"
                f"{dist.atom2.element_symbol}{dist.atom2.index_num+1})={dist.value:.3f}, "
            )

        for angle in angles:
            out_str += (
                f"a({angle.atom1.element_symbol}{angle.atom1.index_num+1}-"
                f"{angle.atom2.element_symbol}{angle.atom2.index_num+1}-"
                f"{angle.atom3.element_symbol}{angle.atom3.index_num+1})={angle.value:.1f}, "
            )

        for torsion in torsions:
            out_str += (
                f"t({torsion.atom1.element_symbol}{torsion.atom1.index_num+1}-"
                f"{torsion.atom2.element_symbol}{torsion.atom2.index_num+1}-"
                f"{torsion.atom3.element_symbol}{torsion.atom3.index_num+1}-"
                f"{torsion.atom4.element_symbol}{torsion.atom4.index_num+1})={torsion.value:.1f}, "
            )

        for outofplane in outofplanes:
            if abs(outofplane.value) <= 10.0:
                out_str += (
                    f"o({outofplane.atom1.element_symbol}{outofplane.atom1.index_num+1}-"
                    f"{outofplane.atom2.element_symbol}{outofplane.atom2.index_num+1}<"
                    f"{outofplane.atom3.element_symbol}{outofplane.atom3.index_num+1}/"
                    f"{outofplane.atom4.element_symbol}{outofplane.atom4.index_num+1})={outofplane.value:.1f}, "
                )

        self.long_msg_signal.emit(out_str.rstrip(", "))

    def toggle_bonds_for_selected_atoms(self):
        """
        Create and add or remove bonds between selected atoms.
        """
        selected_atoms = list(filter(lambda x: x.selected, self.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self.bond_index(atom1, atom2)
            if idx < 0:
                self.add_bond(atom1, atom2)
            else:
                self.remove_bond(idx)
        self.update()

    def add_bonds_for_selected_atoms(self):
        """
        Create and add bonds between selected atoms.
        """
        selected_atoms = list(filter(lambda x: x.selected, self.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self.bond_index(atom1, atom2)
            if idx < 0:
                self.add_bond(atom1, atom2)
        self.update()

    def remove_bonds_for_selected_atoms(self):
        """
        Remove bonds between selected atoms.
        """
        selected_atoms = list(filter(lambda x: x.selected, self.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self.bond_index(atom1, atom2)
            if idx >= 0:
                self.remove_bond(idx)
        self.update()

    def rebuild_bonds(self, tol: float = -2.0):
        """
        Delete all old bonds and generate new a set of bonds
        """
        if not self._draw_item:
            return None

        ds: AtomicCoordinates = self._draw_item.data().data

        if tol < -1.0:
            tol = self._current_geom_bond_tol
        self.remove_bond_all()
        self._build_bonds(ds, tol)
        self.update()

    def rebuild_bonds_default(self):
        """
        Delete all old bonds and generate new set of bonds using default settings
        """
        self._current_geom_bond_tol = self._config.geom_bond_tol
        self.rebuild_bonds(self._current_geom_bond_tol)

    def rebuild_bonds_dynamic(self):
        dlg = BuildBondsDialog(self._current_geom_bond_tol, self)
        if dlg.exec():
            self._current_geom_bond_tol = dlg.current_tol
        else:
            self.rebuild_bonds(self._current_geom_bond_tol)
