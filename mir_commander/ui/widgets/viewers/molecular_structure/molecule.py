import logging
import math

import numpy as np
from PySide6.QtGui import QVector3D

from mir_commander.core.models import AtomicCoordinates
from mir_commander.ui.utils.opengl.models import cylinder, sphere
from mir_commander.ui.utils.opengl.resource_manager import Mesh, ResourceManager, VertexArrayObject
from mir_commander.ui.utils.opengl.scene import BaseNode, ContainerNode
from mir_commander.ui.utils.opengl.utils import Color4f, normalize_color, compute_vertex_normals, compute_face_normals
from mir_commander.utils.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.utils.chem import atomic_number_to_symbol

from .config import MolecularStructureViewerConfig
from .graphics_items.atom import Atom
from .graphics_items.bond import Bond
from .style import Style

logger = logging.getLogger("MoleculeStructure.Molecule")


class Molecule(ContainerNode):
    def __init__(
        self,
        parent: BaseNode,
        config: MolecularStructureViewerConfig,
        resource_manager: ResourceManager,
    ):
        super().__init__(parent, visible=True)

        self._resource_manager = resource_manager

        self._config = config
        self.style = Style(config)
        self.center = QVector3D(0, 0, 0)
        self.radius = 0

        self._atom_index_under_cursor: None | Atom = None

        self.current_geom_bond_tolerance = config.geom_bond_tolerance
        self.atom_items: list[Atom] = []
        self.bond_items: list[Bond] = []
        self.selected_atom_items: list[Atom] = []

        self.apply_style()

        self._sphere_resource_name = "sphere"
        self._cylinder_resource_name = "cylinder"

        self.init_resources()

    def init_resources(self):
        atom_vao = self._get_atom_vao()
        self._resource_manager.add_vertex_array_object(atom_vao)

        bond_vao = self._get_bond_vao()
        self._resource_manager.add_vertex_array_object(bond_vao)

    def _get_atom_vao(self) -> VertexArrayObject:
        logger.debug("Initializing atom mesh data")

        mesh_quality = self._config.quality.mesh
        stacks, slices = int(sphere.min_stacks * mesh_quality), int(sphere.min_slices * mesh_quality)
        tmp_vertices = sphere.get_vertices(stacks=stacks, slices=slices)
        faces = sphere.get_faces(stacks=stacks, slices=slices)
        vertices = sphere.unwind_vertices(tmp_vertices, faces)
        if self._config.quality.smooth:
            normals = compute_vertex_normals(vertices)
        else:
            normals = compute_face_normals(vertices)

        return VertexArrayObject(self._sphere_resource_name, vertices, normals)

    def _get_bond_vao(self) -> VertexArrayObject:
        logger.debug("Initializing bond mesh data")

        mesh_quality = self._config.quality.mesh
        slices = int(cylinder.min_slices * (mesh_quality))
        tmp_vertices = cylinder.get_vertices(stacks=1, slices=slices, radius=1.0, length=1.0, caps=False)
        faces = cylinder.get_faces(stacks=1, slices=slices, caps=False)
        vertices = cylinder.unwind_vertices(tmp_vertices, faces)
        if self._config.quality.smooth:
            normals = compute_vertex_normals(vertices)
        else:
            normals = compute_face_normals(vertices)

        return VertexArrayObject(self._cylinder_resource_name, vertices, normals)

    def build(self, atomic_coordinates: AtomicCoordinates):
        """
        Builds molecule graphics object from `AtomicCoordinates` data structure
        """

        center = QVector3D(
            np.sum(atomic_coordinates.x) / len(atomic_coordinates.x),
            np.sum(atomic_coordinates.y) / len(atomic_coordinates.y),
            np.sum(atomic_coordinates.z) / len(atomic_coordinates.z),
        )

        self.radius = 0

        # add atoms
        for i, atomic_num in enumerate(atomic_coordinates.atomic_num):
            position = QVector3D(atomic_coordinates.x[i], atomic_coordinates.y[i], atomic_coordinates.z[i])
            atom = self.add_atom(i, atomic_num, position)

            d = position.distanceToPoint(center) + atom.radius
            if self.radius < d:
                self.radius = d

        # add bonds
        self.build_bonds(atomic_coordinates, self.current_geom_bond_tolerance)

        self.set_translation(-center)

    def apply_style(self):
        self._apply_atoms_style()
        self._apply_bonds_style()

    def _apply_atoms_style(self):
        # update items
        for atom in self.atom_items:
            radius, color = self._get_atom_radius_and_color(atom.atomic_num)
            atom.set_selected_atom_config(self.style.current.selected_atom)
            atom.set_label_config(self.style.current.atoms.label)
            atom.set_radius(radius)
            atom.set_color(color)

    def _get_atom_radius_and_color(self, atomic_num: int) -> tuple[float, Color4f]:
        atoms_radius = self.style.current.atoms.radius
        if atoms_radius == "atomic":
            if atomic_num >= 0:
                radius = self.style.current.atoms.atomic_radius[atomic_num]
            else:
                radius = self.style.current.atoms.special_atoms.atomic_radius[atomic_num]
            radius *= self.style.current.atoms.scale_factor
        elif atoms_radius == "bond":
            radius = self.style.current.bond.radius
        else:
            raise ValueError(f"Invalid atoms.radius '{atoms_radius}' in style '{self.style.current.name}'")

        if atomic_num >= 0:
            color = self.style.current.atoms.atomic_color[atomic_num]
        else:
            color = self.style.current.atoms.special_atoms.atomic_color[atomic_num]

        return radius, normalize_color(color)

    def _apply_bonds_style(self):
        # update items
        for bond in self.bond_items:
            bond.set_radius(self.style.current.bond.radius)

            if self.style.current.bond.color == "atoms":
                bond.set_atoms_color(True)
            else:
                bond.set_color(normalize_color(self.style.current.bond.color))

    def clear(self):
        self.atom_items.clear()
        self.bond_items.clear()
        self.clear()

    def build_bonds(self, atomic_coordinates: AtomicCoordinates, geom_bond_tolerance: float):
        for i in range(len(atomic_coordinates.atomic_num)):
            if atomic_coordinates.atomic_num[i] < 1:
                continue
            crad_i = ATOM_SINGLE_BOND_COVALENT_RADIUS[atomic_coordinates.atomic_num[i]]
            for j in range(i):
                if atomic_coordinates.atomic_num[j] < 1:
                    continue
                crad_j = ATOM_SINGLE_BOND_COVALENT_RADIUS[atomic_coordinates.atomic_num[j]]
                crad_sum = crad_i + crad_j
                dist_ij = math.sqrt((atomic_coordinates.x[i] - atomic_coordinates.x[j]) ** 2 + (atomic_coordinates.y[i] - atomic_coordinates.y[j]) ** 2 + (atomic_coordinates.z[i] - atomic_coordinates.z[j]) ** 2)
                if dist_ij < (crad_sum + crad_sum * geom_bond_tolerance):
                    self.add_bond(self.atom(i), self.atom(j))

    def add_atom(self, index_num: int, atomic_num: int, position: QVector3D) -> Atom:
        radius, color = self._get_atom_radius_and_color(atomic_num)

        item = Atom(
            self,
            self._sphere_resource_name,
            index_num,
            atomic_num,
            atomic_number_to_symbol(atomic_num),
            position,
            radius,
            color,
            selected_atom_config=self.style.current.selected_atom,
            label_config=self.style.current.atoms.label,
        )
        self.atom_items.append(item)

        return item

    def add_bond(self, atom_1: Atom, atom_2: Atom) -> Bond:
        atoms_color = self.style.current.bond.color == "atoms"
        if atoms_color:
            color = (0.5, 0.5, 0.5, 1.0)
        else:
            color = normalize_color(self.style.current.bond.color)

        item = Bond(
            self,
            self._cylinder_resource_name,
            atom_1,
            atom_2,
            self.style.current.bond.radius,
            atoms_color,
            color,
        )
        self.bond_items.append(item)

        return item

    def remove_bond(self, index: int):
        self.remove_node(self.bond_items[index])
        self.bond_items.pop(index)

    def remove_bond_all(self):
        for bond in self.bond_items:
            self.remove_node(bond)
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

    def highlight_atom_under_cursor(self, atom: None | Atom) -> bool:
        old_atom = self._atom_index_under_cursor
        self._atom_index_under_cursor = atom

        if atom == old_atom:
            return False

        if atom is not None:
            atom.set_under_cursor(True)
        if old_atom is not None:
            old_atom.set_under_cursor(False)

        return True
