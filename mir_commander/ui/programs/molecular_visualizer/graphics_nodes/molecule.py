import logging
import math
from itertools import combinations
from typing import Generator

import numpy as np
from pydantic_extra_types.color import Color
from PySide6.QtGui import QVector3D

from mir_commander.core.project_nodes.atomic_coordinates import AtomicCoordinatesData
from mir_commander.ui.utils.opengl.scene import Node, NodeType
from mir_commander.ui.utils.opengl.utils import Color4f, normalize_color
from mir_commander.utils.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.utils.math import geom_angle_xyz, geom_distance_xyz, geom_oop_angle_xyz, geom_torsion_angle_xyz

from ..config import AtomLabelConfig, Style
from ..errors import CalcError
from ..utils import InteratomicAngle, InteratomicDistance, InteratomicOutOfPlane, InteratomicTorsion
from .atom.atom import Atom
from .bond import Bond

logger = logging.getLogger("MoleculeStructureViewer.GraphicsNodes.Molecule")


class Molecule(Node):
    def __init__(
        self,
        tree_item_id: int,
        atomic_coordinates: AtomicCoordinatesData,
        geom_bond_tolerance: float,
        style: Style,
        atom_label_config: AtomLabelConfig,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs | dict(node_type=NodeType.CONTAINER))

        self._tree_item_id = tree_item_id
        self._atomic_coordinates = atomic_coordinates
        self._geom_bond_tolerance = geom_bond_tolerance
        self._style = style
        self._atom_label_config = atom_label_config

        self.radius: float = 0

        self.atom_items: list[Atom] = []

        self.build()

    @property
    def center(self) -> QVector3D:
        if len(self._atomic_coordinates.x) == 0:
            return QVector3D(0, 0, 0)

        return QVector3D(
            np.sum(self._atomic_coordinates.x) / len(self._atomic_coordinates.x),
            np.sum(self._atomic_coordinates.y) / len(self._atomic_coordinates.y),
            np.sum(self._atomic_coordinates.z) / len(self._atomic_coordinates.z),
        )

    @property
    def tree_item_id(self) -> int:
        return self._tree_item_id

    @property
    def name(self) -> str:
        return "Molecule"

    @property
    def bonds(self) -> Generator[Bond, None, None]:
        for child in self.children:
            if isinstance(child, Bond):
                yield child

    @property
    def _selected_atoms(self) -> list[Atom]:
        return sorted((atom for atom in self.atom_items if atom.selected), key=lambda x: x.selection_update)

    @property
    def is_all_labels_visible_for_selected_atoms(self) -> bool:
        for atom in self.atom_items:
            if atom.selected and not atom.label.visible:
                return False
        return True

    @property
    def is_all_labels_visible(self) -> bool:
        for atom in self.atom_items:
            if not atom.label.visible:
                return False
        return True

    def _get_atom(self, atom_index: int) -> Atom:
        try:
            return self.atom_items[atom_index]
        except IndexError:
            raise IndexError(f"Atom with index {atom_index} not found")

    def build(self):
        """
        Builds molecule graphics object from `AtomicCoordinates` data structure
        """

        if len(self._atomic_coordinates.atomic_num) == 0:
            logger.debug("Can't build molecule because AtomicCoordinates is empty")
            return

        loaded = len(self.atom_items)

        # add atoms
        self._load_atoms()

        # add bonds
        if loaded == 0:
            self._build_all_bonds()
        else:
            self._build_bonds_for_atoms(loaded)

    def _load_atoms(self):
        center = self.center
        loaded = len(self.atom_items)
        total = len(self._atomic_coordinates.atomic_num)

        for index in range(loaded, total):
            atom = self.add_atom(index)
            d = atom.position.distanceToPoint(center) + atom.radius
            if self.radius < d:
                self.radius = d

    def remove_atoms(self, indices: list[int]):
        for index in sorted(indices, reverse=True):
            try:
                self.atom_items.pop(index).remove()
            except IndexError:
                logger.error("Failed to remove atom with index %s", index)

        # TODO: update self.radius

        for i, atom in enumerate(self.atom_items):
            atom.set_index_number(i)

    def update_atomic_number(self, atom_index: int):
        atom = self._get_atom(atom_index)

        atomic_number = self._atomic_coordinates.atomic_num[atom_index]

        if atom.atomic_num == atomic_number:
            return

        radius, color = self._get_atom_radius_and_color(atomic_number)

        atom.set_radius(radius)
        atom.set_color(color)
        atom.set_atomic_number(atomic_number)

        self.rebuild_bonds()

    def update_atom_position(self, atom_index: int):
        atom = self._get_atom(atom_index)
        atom.set_position(
            QVector3D(
                self._atomic_coordinates.x[atom_index],
                self._atomic_coordinates.y[atom_index],
                self._atomic_coordinates.z[atom_index],
            )
        )
        self.rebuild_bonds()

    def select_all_atoms(self):
        for atom in self.atom_items:
            atom.set_selected(True)

    def unselect_all_atoms(self):
        for atom in self.atom_items:
            atom.set_selected(False)

    def select_toggle_all_atoms(self):
        for atom in self.atom_items:
            if atom.selected:
                self.unselect_all_atoms()
                break
        else:
            self.select_all_atoms()

    def cloak_selected_atoms(self):
        for atom in self.atom_items:
            if atom.selected:
                atom.set_cloaked(True)

    def cloak_not_selected_atoms(self):
        for atom in self.atom_items:
            if not atom.selected:
                atom.set_cloaked(True)

    def cloak_h_atoms(self):
        for atom in self.atom_items:
            if atom.atomic_num == 1:
                atom.set_cloaked(True)

    def cloak_not_selected_h_atoms(self):
        for atom in self.atom_items:
            if atom.atomic_num == 1 and not atom.selected:
                atom.set_cloaked(True)

    def cloak_toggle_h_atoms(self):
        for atom in self.atom_items:
            if atom.atomic_num == 1:
                atom.set_cloaked(not atom.cloaked)

    def uncloak_all_atoms(self):
        for atom in self.atom_items:
            atom.set_cloaked(False)

    def cloak_atoms_by_atnum(self, atomic_num: int):
        for atom in self.atom_items:
            if atom.atomic_num == atomic_num:
                atom.set_cloaked(True)

    def show_labels_for_all_atoms(self):
        for atom in self.atom_items:
            atom.set_label_visible(True)

    def hide_labels_for_all_atoms(self):
        for atom in self.atom_items:
            atom.set_label_visible(False)

    def show_labels_for_selected_atoms(self):
        for atom in self.atom_items:
            if atom.selected:
                atom.set_label_visible(True)

    def hide_labels_for_selected_atoms(self):
        for atom in self.atom_items:
            if atom.selected:
                atom.set_label_visible(False)

    def set_style(self, style: Style):
        self._style = style
        self._apply_atoms_style()
        self._apply_bonds_style()

    def set_atom_symbol_visible(self, value: bool):
        for atom in self.atom_items:
            atom.set_symbol_visible(value)

    def set_atom_number_visible(self, value: bool):
        for atom in self.atom_items:
            atom.set_number_visible(value)

    def set_label_size_for_all_atoms(self, size: int):
        for atom in self.atom_items:
            atom.set_label_size(size)

    def set_label_offset_for_all_atoms(self, offset: float):
        for atom in self.atom_items:
            atom.set_label_offset(offset)

    def _apply_atoms_style(self):
        # update items
        for atom in self.atom_items:
            radius, color = self._get_atom_radius_and_color(atom.atomic_num)
            atom.set_selected_atom_config(self._style.selected_atom)
            atom.set_radius(radius)
            atom.set_color(color)

    def _get_atom_radius_and_color(self, atomic_num: int) -> tuple[float, Color4f]:
        atoms_radius = self._style.atoms.radius
        if atoms_radius == "atomic":
            if atomic_num >= 0:
                radius = self._style.atoms.atomic_radius[atomic_num]
            else:
                radius = self._style.atoms.special_atoms.atomic_radius[atomic_num]
            radius *= self._style.atoms.scale_factor
        elif atoms_radius == "bond":
            radius = self._style.bond.radius
        else:
            raise ValueError(f"Invalid atoms.radius '{atoms_radius}' in style '{self._style.name}'")

        if atomic_num >= 0:
            color = self._style.atoms.atomic_color[atomic_num]
        else:
            color = self._style.atoms.special_atoms.atomic_color[atomic_num]

        return radius, normalize_color(color)

    def _apply_bonds_style(self):
        # update items
        for bond in self.bonds:
            bond.set_radius(self._style.bond.radius)

            if self._style.bond.color == "atoms":
                bond.set_atoms_color(True)
            else:
                bond.set_color(normalize_color(self._style.bond.color))  # type: ignore[arg-type]

    def clear(self):
        self.atom_items.clear()
        super().clear()

    def swap_atoms_indices(self, index_1: int, index_2: int):
        self.atom_items[index_1].set_index_number(index_2)
        self.atom_items[index_2].set_index_number(index_1)
        self.atom_items[index_1], self.atom_items[index_2] = self.atom_items[index_2], self.atom_items[index_1]

    def _build_bonds_for_atoms(self, start_index: int):
        for index in range(start_index, len(self.atom_items)):
            atom = self.atom_items[index]
            if atom.atomic_num < 1:
                continue

            atom_crad = ATOM_SINGLE_BOND_COVALENT_RADIUS[atom.atomic_num]
            for index_2 in range(index):
                other_atom = self.atom_items[index_2]
                if other_atom.atomic_num < 1 or atom == other_atom:
                    continue

                other_atom_crad = ATOM_SINGLE_BOND_COVALENT_RADIUS[other_atom.atomic_num]
                crad_sum = atom_crad + other_atom_crad
                dist = atom.position.distanceToPoint(other_atom.position)
                if dist < crad_sum + crad_sum * self._geom_bond_tolerance:
                    self.add_bond(atom, other_atom)

    def _build_all_bonds(self):
        atomic_num = np.array(self._atomic_coordinates.atomic_num)
        x = np.array(self._atomic_coordinates.x)
        y = np.array(self._atomic_coordinates.y)
        z = np.array(self._atomic_coordinates.z)
        atom_single_bond_covalent_radius = np.array(
            [ATOM_SINGLE_BOND_COVALENT_RADIUS[i] if i > 0 else 0 for i in atomic_num]
        )

        for i in range(len(atomic_num)):
            if atomic_num[i] < 1:
                continue

            crad_i = atom_single_bond_covalent_radius[i]
            j_indices = np.arange(i)
            valid_j = atomic_num[:i] >= 1

            if not np.any(valid_j):
                continue

            crad_j = atom_single_bond_covalent_radius[:i][valid_j]
            crad_sum = crad_i + crad_j

            dx = x[i] - x[:i][valid_j]
            dy = y[i] - y[:i][valid_j]
            dz = z[i] - z[:i][valid_j]

            dist_ij = np.sqrt(dx * dx + dy * dy + dz * dz)
            threshold = crad_sum + crad_sum * self._geom_bond_tolerance

            bonded = dist_ij < threshold
            j_valid_indices = j_indices[valid_j][bonded]

            for j in j_valid_indices:
                self.add_bond(self.atom(i), self.atom(j))

    def rebuild_bonds(self):
        self.remove_all_bonds()
        self._build_all_bonds()

    def add_atom(self, index: int) -> Atom:
        atomic_num = self._atomic_coordinates.atomic_num[index]
        radius, color = self._get_atom_radius_and_color(atomic_num)
        position = QVector3D(
            self._atomic_coordinates.x[index], self._atomic_coordinates.y[index], self._atomic_coordinates.z[index]
        )

        item = Atom(
            index,
            atomic_num,
            position,
            radius,
            color,
            selected_atom_config=self._style.selected_atom,
            label_config=self._atom_label_config,
            parent=self,
        )
        self.atom_items.append(item)

        return item

    def add_bond(self, atom_1: Atom, atom_2: Atom):
        if atom_1 == atom_2:
            raise ValueError(f"The same atom {atom_1.index} cannot be bonded to itself")

        if type(self._style.bond.color) is Color:
            color = normalize_color(self._style.bond.color)
            atoms_color = False
        else:
            color = (0.5, 0.5, 0.5, 1.0)
            atoms_color = True

        Bond(
            atom_1,
            atom_2,
            self._style.bond.radius,
            atoms_color,
            color,
            parent=self,
        )

    def remove_all_bonds(self):
        for child in self.children.copy():
            if isinstance(child, Bond):
                child.remove()

    def atom(self, index: int) -> Atom:
        return self.atom_items[index]

    def get_bond(self, atom_1: Atom, atom_2: Atom) -> Bond:
        """
        Get the bond between atoms atom1 and atom2.
        """

        if atom_1 == atom_2:
            raise ValueError(f"The same atom {atom_1.id} cannot be bonded to itself")

        for bond_1 in atom_1.related_bonds:
            for bond_2 in atom_2.related_bonds:
                if bond_1.id == bond_2.id:
                    return bond_1
        raise ValueError(f"No bond found between atoms {atom_1.id} and {atom_2.id}")

    def calc_auto_lastsel_atoms(self) -> str:
        """
        Calculate and print internal geometrical parameter,
        distance, angle or torsion angle, depending on the number of selected atoms.
        """

        match len(self._selected_atoms):
            case 2:
                return self.calc_distance_last2sel_atoms()
            case 3:
                return self.calc_angle_last3sel_atoms()
            case 4:
                return self.calc_torsion_last4sel_atoms()
            case _:
                raise CalcError("Two, three or four atoms must be selected!")

    def calc_distance_last2sel_atoms(self) -> str:
        """
        Calculate and print distance (in internal units) between last two selected atoms.
        """

        atoms = self._selected_atoms
        if len(atoms) >= 2:
            atom1 = atoms[-2]
            atom2 = atoms[-1]
            pos1 = atom1.position
            pos2 = atom2.position
            distance = geom_distance_xyz(pos1.x(), pos1.y(), pos1.z(), pos2.x(), pos2.y(), pos2.z())
            return f"r({atom1.element_symbol}{atom1.index + 1}-{atom2.element_symbol}{atom2.index + 1})={distance:.3f}"
        else:
            raise CalcError("At least two atoms must be selected!")

    def calc_angle_last3sel_atoms(self) -> str:
        """
        Calculate and print angle (in degrees) formed by last three selected atoms: a1-a2-a3
        """

        atoms = self._selected_atoms
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
            return (
                f"a({atom1.element_symbol}{atom1.index + 1}-{atom2.element_symbol}{atom2.index + 1}-"
                f"{atom3.element_symbol}{atom3.index + 1})={angle:.1f}"
            )
        else:
            raise CalcError("At least three atoms must be selected!")

    def calc_torsion_last4sel_atoms(self) -> str:
        """
        Calculate and print torsion angle (in degrees) formed by last four selected atoms: a1-a2-a3-a4
        """

        atoms = self._selected_atoms
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
            return (
                f"t({atom1.element_symbol}{atom1.index + 1}-{atom2.element_symbol}{atom2.index + 1}-"
                f"{atom3.element_symbol}{atom3.index + 1}-{atom4.element_symbol}{atom4.index + 1})={angle:.1f}"
            )
        else:
            raise CalcError("At least four atoms must be selected!")

    def calc_oop_last4sel_atoms(self) -> str:
        """
        Calculate and print out-of-plane angle (in degrees) formed by last four selected atoms: a1-a2-a3-a4
        """

        atoms = self._selected_atoms
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
            return (
                f"o({atom1.element_symbol}{atom1.index + 1}-{atom2.element_symbol}{atom2.index + 1}<"
                f"{atom3.element_symbol}{atom3.index + 1}/{atom4.element_symbol}{atom4.index + 1})={angle:.1f}"
            )
        else:
            raise CalcError("At least four atoms must be selected!")

    def calc_all_parameters_selected_atoms(self) -> str:
        """
        Calculate and print all parameters formed by all selected atoms
        """

        distances: list[InteratomicDistance] = []
        angles: list[InteratomicAngle] = []
        torsions: list[InteratomicTorsion] = []
        outofplanes: list[InteratomicOutOfPlane] = []

        # Generate list of distances, which are bonds formed by selected atoms
        for bond in self.bonds:
            atom_1, atom_2 = bond.atoms
            if atom_1.selected and atom_2.selected:
                distances.append(InteratomicDistance(atom_1, atom_2))

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
                f"r({dist.atom1.element_symbol}{dist.atom1.index + 1}-"
                f"{dist.atom2.element_symbol}{dist.atom2.index + 1})={dist.value:.3f}, "
            )

        for angle in angles:
            out_str += (
                f"a({angle.atom1.element_symbol}{angle.atom1.index + 1}-"
                f"{angle.atom2.element_symbol}{angle.atom2.index + 1}-"
                f"{angle.atom3.element_symbol}{angle.atom3.index + 1})={angle.value:.1f}, "
            )

        for torsion in torsions:
            out_str += (
                f"t({torsion.atom1.element_symbol}{torsion.atom1.index + 1}-"
                f"{torsion.atom2.element_symbol}{torsion.atom2.index + 1}-"
                f"{torsion.atom3.element_symbol}{torsion.atom3.index + 1}-"
                f"{torsion.atom4.element_symbol}{torsion.atom4.index + 1})={torsion.value:.1f}, "
            )

        for outofplane in outofplanes:
            if abs(outofplane.value) <= 10.0:
                out_str += (
                    f"o({outofplane.atom1.element_symbol}{outofplane.atom1.index + 1}-"
                    f"{outofplane.atom2.element_symbol}{outofplane.atom2.index + 1}<"
                    f"{outofplane.atom3.element_symbol}{outofplane.atom3.index + 1}/"
                    f"{outofplane.atom4.element_symbol}{outofplane.atom4.index + 1})={outofplane.value:.1f}, "
                )

        return out_str.rstrip(", ")

    def toggle_bonds_for_selected_atoms(self):
        """
        Create and add or remove bonds between selected atoms.
        """

        selected_atoms = list(filter(lambda x: x.selected, self.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            try:
                self.get_bond(atom1, atom2).remove()
            except ValueError:
                self.add_bond(atom1, atom2)

    def add_bonds_for_selected_atoms(self):
        """
        Create and add bonds between selected atoms.
        """

        selected_atoms = list(filter(lambda x: x.selected, self.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            try:
                self.get_bond(atom1, atom2)
            except ValueError:
                self.add_bond(atom1, atom2)

    def remove_bonds_for_selected_atoms(self):
        """
        Remove bonds between selected atoms.
        """

        selected_atoms = list(filter(lambda x: x.selected, self.atom_items))
        for atom1, atom2 in combinations(selected_atoms, 2):
            try:
                self.get_bond(atom1, atom2).remove()
            except ValueError:
                pass

    def set_geom_bond_tolerance(self, geom_bond_tolerance: float = -2.0):
        """
        Delete all old bonds and generate new a set of bonds
        """

        if geom_bond_tolerance < -1.0:
            geom_bond_tolerance = self._geom_bond_tolerance
        self._geom_bond_tolerance = geom_bond_tolerance
        self.rebuild_bonds()
