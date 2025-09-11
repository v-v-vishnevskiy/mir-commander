import math
from collections import defaultdict
from itertools import combinations
from typing import cast

from PySide6.QtCore import QPoint
from PySide6.QtGui import QContextMenuEvent, QVector3D
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget

from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.opengl.errors import Error, NodeNotFoundError
from mir_commander.ui.utils.opengl.keymap import Keymap
from mir_commander.ui.utils.opengl.opengl_widget import OpenGLWidget
from mir_commander.ui.utils.opengl.resource_manager import FragmentShader, ShaderProgram, VertexShader
from mir_commander.ui.utils.opengl.text_overlay import TextOverlay
from mir_commander.ui.utils.opengl.utils import normalize_color
from mir_commander.ui.utils.viewer import Viewer
from mir_commander.ui.utils.widget import TR
from mir_commander.utils.chem import symbol_to_atomic_number
from mir_commander.utils.math import geom_angle_xyz, geom_distance_xyz, geom_oop_angle_xyz, geom_torsion_angle_xyz

from . import shaders
from .build_bonds_dialog import BuildBondsDialog
from .config import AtomLabelType
from .context_menu import ContextMenu
from .graphics_nodes import Atom, BaseGraphicsNode, Molecule
from .save_image_dialog import SaveImageDialog
from .utils import InteratomicAngle, InteratomicDistance, InteratomicOutOfPlane, InteratomicTorsion


class AtomicCoordinatesViewer(OpenGLWidget):
    def __init__(self, parent: QWidget, atomic_coordinates: AtomicCoordinates, app_config: AppConfig, title: str):
        super().__init__(
            parent=parent,
            keymap=Keymap(app_config.project_window.widgets.viewers.molecular_structure.keymap.viewer.model_dump()),
        )

        self.config = app_config.project_window.widgets.viewers.molecular_structure.model_copy(deep=True)
        self._title = title

        self._atomic_coordinates: AtomicCoordinates = atomic_coordinates

        self._node_under_cursor: BaseGraphicsNode | None = None
        self._selected_nodes: defaultdict[type[BaseGraphicsNode], list[BaseGraphicsNode]] = defaultdict(list)

        self._molecule = Molecule(self.resource_manager.current_scene.root_node, app_config)
        self._molecule.build(self._atomic_coordinates)

        self._under_cursor_overlay = TextOverlay(
            parent=self,
            config=self._molecule.style.current.under_cursor_text_overlay,
        )
        self._under_cursor_overlay.hide()

        self._context_menu = ContextMenu(parent=self, app_config=app_config)

    def init_actions(self):
        super().init_actions()
        self.action_handler.add_action("toggle_node_selection", False, self.toggle_node_selection_under_cursor)

    def init_shaders(self):
        super().init_shaders()
        self.resource_manager.add_shader(
            ShaderProgram(
                "atom_label", VertexShader(shaders.vertex.ATOM_LABEL), FragmentShader(shaders.fragment.ATOM_LABEL)
            )
        )

    def initializeGL(self):
        super().initializeGL()

        self.set_background_color(normalize_color(self._molecule.style.current.background.color))

        # Add VAOs to resource manager
        self.resource_manager.add_vertex_array_object(self._molecule.get_atom_vao())
        self.resource_manager.add_vertex_array_object(self._molecule.get_bond_vao())

        self.projection_manager.orthographic_projection.set_view_bounds(
            self._molecule.radius + self._molecule.radius * 0.10
        )

        current_fov = self._molecule.style.current.projection.perspective.fov
        self.set_perspective_projection_fov(current_fov)
        fov_factor = current_fov / 45.0
        self.projection_manager.perspective_projection.set_near_far_plane(
            self._molecule.radius / fov_factor,
            8 * self._molecule.radius / fov_factor,
        )
        self.set_projection_mode(self._molecule.style.current.projection.mode)

        self.resource_manager.current_camera.reset_to_default()
        self.resource_manager.current_camera.set_position(QVector3D(0, 0, 3 * self._molecule.radius / fov_factor))

    def set_atomic_coordinates(self, atomic_coordinates: AtomicCoordinates):
        self._atomic_coordinates = atomic_coordinates
        self._molecule.build(self._atomic_coordinates)
        self.update()

    def set_title(self, title: str):
        self._title = title

    def toggle_node_selection_under_cursor(self):
        try:
            node = self.node_under_cursor()
            item = node.parent
            if node.toggle_selection():
                self._selected_nodes[item.__class__].append(item)
            else:
                self._selected_nodes[item.__class__].remove(item)
            self.update()
        except (NodeNotFoundError, ValueError):
            # ValueError is raised when node is not found in `_selected_nodes`
            pass

    def new_cursor_position(self, x: int, y: int):
        self._handle_node_under_cursor(x, y)

    def _handle_node_under_cursor(self, x: int, y: int):
        if self._node_under_cursor is not None:
            self._node_under_cursor.set_under_cursor(False)

        try:
            node_under_cursor = cast(BaseGraphicsNode, self.node_under_cursor())
            node_under_cursor.set_under_cursor(True)
            self._node_under_cursor = node_under_cursor

            if text := node_under_cursor.get_text():
                self._under_cursor_overlay.set_text(text)
                size = self._under_cursor_overlay.size()
                self._under_cursor_overlay.set_position(QPoint(x, y - size.height()))
                self._under_cursor_overlay.show()
            else:
                self._under_cursor_overlay.set_text("")
                self._under_cursor_overlay.hide()
        except NodeNotFoundError:
            if self._node_under_cursor is not None:
                self._node_under_cursor.set_under_cursor(False)
                self._node_under_cursor = None
            self._under_cursor_overlay.set_text("")
            self._under_cursor_overlay.hide()
        self.update()

    def contextMenuEvent(self, event: QContextMenuEvent):
        self._context_menu.exec(event.globalPos())

    def save_img_action_handler(self):
        dlg = SaveImageDialog(self, self.size().width(), self.size().height(), self._title)
        if dlg.exec():
            save_flag = True
            if dlg.img_file_path.exists():
                ret = QMessageBox.warning(
                    self,
                    self.tr("Save image"),
                    self.tr("The file already exists:")
                    + f"\n{dlg.img_file_path}\n"
                    + self.tr("Do you want to overwrite it?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if ret != QMessageBox.StandardButton.Yes:
                    save_flag = False

            if save_flag:
                image = None
                try:
                    image = self.render_to_image(dlg.img_width, dlg.img_height, dlg.transparent_bg, dlg.crop_to_content)
                except Error as e:
                    message_box = QMessageBox(
                        QMessageBox.Icon.Critical,
                        self.tr("Error image rendering"),
                        self.tr("Cannot create image."),
                        QMessageBox.StandardButton.Close,
                    )
                    message_box.setDetailedText(str(e))
                    message_box.exec()

                if image is not None:
                    if image.save(str(dlg.img_file_path)):
                        parent = cast(Viewer, self.parent())
                        parent.short_msg_signal.emit(TR.tr("Image saved"))
                    else:
                        QMessageBox.critical(
                            self,
                            self.tr("Save image"),
                            self.tr("Could not save image:")
                            + f"\n{dlg.img_file_path}\n"
                            + self.tr("The path does not exist or is write-protected."),
                        )

    def set_next_style(self):
        if self._molecule.style.set_next_style():
            self._molecule.apply_style()
            self._under_cursor_overlay.set_config(
                self._molecule.style.current.under_cursor_text_overlay, skip_position=True
            )
            self.update()

    def set_prev_style(self):
        if self._molecule.style.set_prev_style():
            self._molecule.apply_style()
            self._under_cursor_overlay.set_config(
                self._molecule.style.current.under_cursor_text_overlay, skip_position=True
            )
            self.update()

    def select_all_atoms(self):
        for atom in self._molecule.atom_items:
            atom.set_selected(True)
        self._selected_nodes[Atom] = self._molecule.atom_items.copy()
        self.update()

    def unselect_all_atoms(self):
        for atom in self._molecule.atom_items:
            atom.set_selected(False)
        self._selected_nodes[Atom] = []
        self.update()

    def select_toggle_all_atoms(self):
        """
        Unselect all atoms if at least one atom selected,
        otherwise select all.
        """

        if len(self._selected_nodes[Atom]) > 0:
            self.unselect_all_atoms()
        else:
            self.select_all_atoms()

    def cloak_selected_atoms(self):
        for atom in self._molecule.atom_items:
            if atom._selected:
                atom.set_cloaked(True)
        self.update()

    def cloak_not_selected_atoms(self):
        for atom in self._molecule.atom_items:
            if not atom._selected:
                atom.set_cloaked(True)
        self.update()

    def cloak_h_atoms(self):
        for atom in self._molecule.atom_items:
            if atom.atomic_num == 1:
                atom.set_cloaked(True)
        self.update()

    def cloak_not_selected_h_atoms(self):
        for atom in self._molecule.atom_items:
            if atom.atomic_num == 1 and not atom._selected:
                atom.set_cloaked(True)
        self.update()

    def cloak_toggle_h_atoms(self):
        for atom in self._molecule.atom_items:
            if atom.atomic_num == 1:
                atom.set_cloaked(not atom.cloaked)
        self.update()

    def uncloak_all_atoms(self):
        for atom in self._molecule.atom_items:
            atom.set_cloaked(False)
        self.update()

    def _cloak_atoms_by_atnum(self, atomic_num: int):
        for atom in self._molecule.atom_items:
            if atom.atomic_num == atomic_num:
                atom.set_cloaked(True)
        self.update()

    def cloak_atoms_by_atnum(self):
        el_symbol, ok = QInputDialog.getText(
            self, self.tr("Cloak atoms by type"), self.tr("Enter element symbol:"), QLineEdit.Normal, ""
        )
        if ok:
            try:
                self._cloak_atoms_by_atnum(symbol_to_atomic_number(el_symbol))
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

        atoms = self._selected_nodes[Atom]
        if len(atoms) >= 2:
            atom1 = atoms[-2]
            atom2 = atoms[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            distance = geom_distance_xyz(pos1.x(), pos1.y(), pos1.z(), pos2.x(), pos2.y(), pos2.z())
            self.parent().long_msg_signal.emit(
                f"r({atom1.element_symbol}{atom1.index_num + 1}-{atom2.element_symbol}{atom2.index_num + 1})={distance:.3f}"
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

        atoms = self._selected_nodes[Atom]
        if len(atoms) >= 3:
            atom1 = atoms[-3]
            atom2 = atoms[-2]
            atom3 = atoms[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            pos3 = atom3.position
            angle = geom_angle_xyz(
                pos1.x(), pos1.y(), pos1.z(), pos2.x(), pos2.y(), pos2.z(), pos3.x(), pos3.y(), pos3.z()
            ) * (180.0 / math.pi)
            self.parent().long_msg_signal.emit(
                f"a({atom1.element_symbol}{atom1.index_num + 1}-{atom2.element_symbol}{atom2.index_num + 1}-"
                f"{atom3.element_symbol}{atom3.index_num + 1})={angle:.1f}"
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

        atoms = self._selected_nodes[Atom]
        if len(atoms) >= 4:
            atom1 = atoms[-4]
            atom2 = atoms[-3]
            atom3 = atoms[-2]
            atom4 = atoms[-1]
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
            self.parent().long_msg_signal.emit(
                f"t({atom1.element_symbol}{atom1.index_num + 1}-{atom2.element_symbol}{atom2.index_num + 1}-"
                f"{atom3.element_symbol}{atom3.index_num + 1}-{atom4.element_symbol}{atom4.index_num + 1})={angle:.1f}"
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

        atoms = self._selected_nodes[Atom]
        if len(atoms) >= 4:
            atom1 = atoms[-4]
            atom2 = atoms[-3]
            atom3 = atoms[-2]
            atom4 = atoms[-1]
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
            self.parent().long_msg_signal.emit(
                f"o({atom1.element_symbol}{atom1.index_num + 1}-{atom2.element_symbol}{atom2.index_num + 1}<"
                f"{atom3.element_symbol}{atom3.index_num + 1}/{atom4.element_symbol}{atom4.index_num + 1})={angle:.1f}"
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

        num_selected = len(self._selected_nodes[Atom])
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
        for bond in self._molecule.bond_items:
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
                f"r({dist.atom1.element_symbol}{dist.atom1.index_num + 1}-"
                f"{dist.atom2.element_symbol}{dist.atom2.index_num + 1})={dist.value:.3f}, "
            )

        for angle in angles:
            out_str += (
                f"a({angle.atom1.element_symbol}{angle.atom1.index_num + 1}-"
                f"{angle.atom2.element_symbol}{angle.atom2.index_num + 1}-"
                f"{angle.atom3.element_symbol}{angle.atom3.index_num + 1})={angle.value:.1f}, "
            )

        for torsion in torsions:
            out_str += (
                f"t({torsion.atom1.element_symbol}{torsion.atom1.index_num + 1}-"
                f"{torsion.atom2.element_symbol}{torsion.atom2.index_num + 1}-"
                f"{torsion.atom3.element_symbol}{torsion.atom3.index_num + 1}-"
                f"{torsion.atom4.element_symbol}{torsion.atom4.index_num + 1})={torsion.value:.1f}, "
            )

        for outofplane in outofplanes:
            if abs(outofplane.value) <= 10.0:
                out_str += (
                    f"o({outofplane.atom1.element_symbol}{outofplane.atom1.index_num + 1}-"
                    f"{outofplane.atom2.element_symbol}{outofplane.atom2.index_num + 1}<"
                    f"{outofplane.atom3.element_symbol}{outofplane.atom3.index_num + 1}/"
                    f"{outofplane.atom4.element_symbol}{outofplane.atom4.index_num + 1})={outofplane.value:.1f}, "
                )

        self.parent().long_msg_signal.emit(out_str.rstrip(", "))

    def toggle_bonds_for_selected_atoms(self):
        """
        Create and add or remove bonds between selected atoms.
        """

        selected_atoms = list(filter(lambda x: x.selected, self._molecule.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self._molecule.bond_index(atom1, atom2)
            if idx < 0:
                self._molecule.add_bond(atom1, atom2)
            else:
                self._molecule.remove_bond(idx)
        self.update()

    def add_bonds_for_selected_atoms(self):
        """
        Create and add bonds between selected atoms.
        """

        selected_atoms = list(filter(lambda x: x.selected, self._molecule.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self._molecule.bond_index(atom1, atom2)
            if idx < 0:
                self._molecule.add_bond(atom1, atom2)
        self.update()

    def remove_bonds_for_selected_atoms(self):
        """
        Remove bonds between selected atoms.
        """

        selected_atoms = list(filter(lambda x: x.selected, self._molecule.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self._molecule.bond_index(atom1, atom2)
            if idx >= 0:
                self._molecule.remove_bond(idx)
        self.update()

    def rebuild_bonds(self, tol: float = -2.0):
        """
        Delete all old bonds and generate new a set of bonds
        """

        if tol < -1.0:
            tol = self._molecule.current_geom_bond_tolerance
        self._molecule.remove_bond_all()
        self._molecule.build_bonds(self._atomic_coordinates, tol)
        self.update()

    def rebuild_bonds_default(self):
        """
        Delete all old bonds and generate new set of bonds using default settings
        """

        self._molecule.current_geom_bond_tolerance = self.config.geom_bond_tolerance
        self.rebuild_bonds(self._molecule.current_geom_bond_tolerance)

    def rebuild_bonds_dynamic(self):
        dlg = BuildBondsDialog(self._molecule.current_geom_bond_tolerance, self)
        if dlg.exec():
            self._molecule.current_geom_bond_tolerance = dlg.current_tol
        else:
            self.rebuild_bonds(self._molecule.current_geom_bond_tolerance)

    def atom_labels_show_for_all_atoms(self):
        for atom in self._molecule.atom_items:
            atom.set_label_visible(True)
        self.update()

    def atom_labels_hide_for_all_atoms(self):
        for atom in self._molecule.atom_items:
            atom.set_label_visible(False)
        self.update()

    def atom_labels_show_for_selected_atoms(self):
        for atom in self._selected_nodes[Atom]:
            atom.set_label_visible(True)
        self.update()

    def atom_labels_hide_for_selected_atoms(self):
        for atom in self._selected_nodes[Atom]:
            atom.set_label_visible(False)
        self.update()

    def atom_labels_set_type(self, value: AtomLabelType):
        self.config.atom_label.type = value
        for atom in self._molecule.atom_items:
            atom.set_label_type(value)
        self.update()

    def set_label_size_for_all_atoms(self, size: int):
        self.config.atom_label.size = size
        for atom in self._molecule.atom_items:
            atom.set_label_size(size)
        self.update()

    def set_label_offset_for_all_atoms(self, offset: float):
        self.config.atom_label.offset = offset
        for atom in self._molecule.atom_items:
            atom.set_label_offset(offset)
        self.update()
