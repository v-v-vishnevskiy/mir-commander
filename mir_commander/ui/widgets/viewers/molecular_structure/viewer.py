import logging
import math
from itertools import combinations
from typing import TYPE_CHECKING, Optional

import numpy as np
import OpenGL.error
from PySide6.QtCore import Slot
from PySide6.QtGui import QSurfaceFormat, QVector3D
from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget

from mir_commander.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.utils.opengl.keymap import Keymap
from mir_commander.ui.utils.opengl.widget import Widget
from mir_commander.ui.utils.widget import StatusBar
from mir_commander.utils.chem import symbol_to_atomic_number
from mir_commander.utils.math import geom_angle_xyz, geom_distance_xyz, geom_oop_angle_xyz, geom_torsion_angle_xyz

from .build_bonds_dialog import BuildBondsDialog
from .graphics_items import Atom
from .save_image_dialog import SaveImageDialog
from .scene import Scene
from .style import Style

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow
    from mir_commander.ui.widgets.docks.project_dock.items import Item

logger = logging.getLogger(__name__)


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


class MolecularStructure(Widget):
    def __init__(self, parent: QWidget, item: "Item", main_window: "MainWindow", all: bool = False):
        self._main_window = main_window
        self._config = main_window.config.widgets.viewers.molecular_structure

        project_id = id(main_window.project)
        self._style = Style(self._config)
        keymap = Keymap(project_id, self._config.keymap.model_dump())

        self.geom_bond_tol = self._config.geom_bond_tol

        super().__init__(scene=Scene(self, self._style), keymap=keymap, parent=parent)

        # Define explicitly, otherwise mypy will complain about undefined attributes like "atom" etc.
        self.scene: Scene

        self.setMinimumSize(self._config.min_size[0], self._config.min_size[1])
        self.resize(self._config.size[0], self._config.size[1])

        self.item = item
        self.all = all

        self._keymap.load_from_config(self._config.keymap.model_dump())

        if self._config.antialiasing:
            sf = QSurfaceFormat()
            sf.setSamples(16)
            self.setFormat(sf)

        self._molecule_index = 0
        self._draw_item = None
        self._set_draw_item()

        self.update_window_title()

        self._build_molecule()

    def _init_actions(self):
        super()._init_actions()
        # TODO: document why do we need such a complicated system for managing of actions
        self._actions["item_next"] = (False, self._draw_next_item, tuple())
        self._actions["item_prev"] = (False, self._draw_prev_item, tuple())
        self._actions["style_next"] = (False, self._set_next_style, tuple())
        self._actions["style_prev"] = (False, self._set_prev_style, tuple())
        self._actions["save_image"] = (False, self.save_img_action_handler, tuple())
        self._actions["toggle_atom_selection"] = (False, self.scene.toggle_atom_selection, tuple())

    def _apply_style(self):
        self.scene.apply_style()

    def _atomic_coordinates_item(
        self, index: int, parent: "Item", counter: int = -1
    ) -> tuple[bool, int, Optional["Item"]]:
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
                elif self.all and item.hasChildren():
                    found, counter, item = self._atomic_coordinates_item(index, item, counter)
                    last_item = item
                    if found:
                        return found, counter, item
            return False, counter, last_item

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
            atom = self.scene.add_atom(i, atomic_num, position)

            d = position.length() + atom.radius
            if longest_distance < d:
                longest_distance = d

        # add bonds
        self._build_bonds(ds, self.geom_bond_tol)

        center = QVector3D(np.sum(ds.x) / len(ds.x), np.sum(ds.y) / len(ds.y), np.sum(ds.z) / len(ds.z))
        self.scene.set_center(center)
        self.scene.set_camera_distance(longest_distance - center.length())

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
                    self.scene.add_bond(self.scene.atom(i), self.scene.atom(j))

    def _set_draw_item(self):
        _, self._molecule_index, self._draw_item = self._atomic_coordinates_item(self._molecule_index, self.item)

    def _set_prev_style(self):
        if self._style.set_prev_style():
            self._apply_style()

    def _set_next_style(self):
        if self._style.set_next_style():
            self._apply_style()

    def _draw_prev_item(self):
        if self._molecule_index > 0:
            self._molecule_index -= 1
            self._set_draw_item()
            self.update_window_title()
            self.scene.clear(update=False)
            self._build_molecule()
            self.update()

    def _draw_next_item(self):
        self._molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if id(item) != id(self._draw_item):
            self.update_window_title()
            self.scene.clear(update=False)
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
                    image = self.scene.render_to_image(
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
                        self._main_window.status.showMessage(StatusBar.tr("Image saved"), 10000)
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
                self.scene.cloak_atoms_by_atnum(symbol_to_atomic_number(el_symbol))
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
        if len(self.scene.selected_atom_items) >= 2:
            atom1 = self.scene.selected_atom_items[-2]
            atom2 = self.scene.selected_atom_items[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            distance = geom_distance_xyz(pos1.x(), pos1.y(), pos1.z(), pos2.x(), pos2.y(), pos2.z())
            self._main_window.append_to_console(
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
        if len(self.scene.selected_atom_items) >= 3:
            atom1 = self.scene.selected_atom_items[-3]
            atom2 = self.scene.selected_atom_items[-2]
            atom3 = self.scene.selected_atom_items[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            pos3 = atom3.position
            angle = geom_angle_xyz(
                pos1.x(), pos1.y(), pos1.z(), pos2.x(), pos2.y(), pos2.z(), pos3.x(), pos3.y(), pos3.z()
            ) * (180.0 / math.pi)
            self._main_window.append_to_console(
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
        if len(self.scene.selected_atom_items) >= 4:
            atom1 = self.scene.selected_atom_items[-4]
            atom2 = self.scene.selected_atom_items[-3]
            atom3 = self.scene.selected_atom_items[-2]
            atom4 = self.scene.selected_atom_items[-1]
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
            self._main_window.append_to_console(
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
        if len(self.scene.selected_atom_items) >= 4:
            atom1 = self.scene.selected_atom_items[-4]
            atom2 = self.scene.selected_atom_items[-3]
            atom3 = self.scene.selected_atom_items[-2]
            atom4 = self.scene.selected_atom_items[-1]
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
            self._main_window.append_to_console(
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
        num_selected = len(self.scene.selected_atom_items)
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
        for bond in self.scene.bond_items:
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

        self._main_window.append_to_console(out_str.rstrip(", "))

    def toggle_bonds_for_selected_atoms(self):
        """
        Create and add or remove bonds between selected atoms.
        """
        selected_atoms = list(filter(lambda x: x.selected, self.scene.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self.scene.bond_index(atom1, atom2)
            if idx < 0:
                self.scene.add_bond(atom1, atom2)
            else:
                self.scene.remove_bond(idx)
        self.scene.update()

    def add_bonds_for_selected_atoms(self):
        """
        Create and add bonds between selected atoms.
        """
        selected_atoms = list(filter(lambda x: x.selected, self.scene.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self.scene.bond_index(atom1, atom2)
            if idx < 0:
                self.scene.add_bond(atom1, atom2)
        self.scene.update()

    def remove_bonds_for_selected_atoms(self):
        """
        Remove bonds between selected atoms.
        """
        selected_atoms = list(filter(lambda x: x.selected, self.scene.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            idx = self.scene.bond_index(atom1, atom2)
            if idx >= 0:
                self.scene.remove_bond(idx)
        self.scene.update()

    def rebuild_bonds(self, tol: float = -2.0):
        """
        Delete all old bonds and generate new a set of bonds
        """
        if not self._draw_item:
            return None

        ds: AtomicCoordinates = self._draw_item.data().data

        if tol < -1.0:
            tol = self.geom_bond_tol
        self.scene.remove_bond_all()
        self._build_bonds(ds, tol)
        self.scene.update()

    def rebuild_bonds_default(self):
        """
        Delete all old bonds and generate new set of bonds using default settings
        """
        self.geom_bond_tol = self._config.geom_bond_tol
        self.rebuild_bonds(self.geom_bond_tol)

    def rebuild_bonds_dynamic(self):
        dlg = BuildBondsDialog(self.geom_bond_tol, self)
        if dlg.exec():
            self.geom_bond_tol = dlg.current_tol
        else:
            self.rebuild_bonds(self.geom_bond_tol)
