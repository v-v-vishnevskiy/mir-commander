import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph import Vector
from PySide6.QtCore import QKeyCombination, Qt
from PySide6.QtGui import QKeyEvent

from mir_commander.data_structures.molecule import AtomicCoordinates as AtomicCoordinatesDS
from mir_commander.default_config import CONFIG

if TYPE_CHECKING:
    from mir_commander.utils.item import Item


AT_RAD = CONFIG["widgets"]["viewers"]["molecule"]["atoms"]["radius"]  # type: ignore
COLOR = CONFIG["widgets"]["viewers"]["molecule"]["atoms"]["color"]  # type: ignore
AT_SBCOVRAD = CONFIG["atom_single_bond_covalent_radius"]  # type: ignore


@dataclass
class MoleculeStruct:
    atoms: List[gl.GLMeshItem]
    center: Vector
    radius: float


class Molecule(gl.GLViewWidget):
    def __init__(self, item: "Item"):
        super().__init__(None, rotationMethod="quaternion")
        self.item = item
        self._draw_item = None
        self.__molecule_index = 0
        self.__camera_set = False

        self.__sphere_mesh_data = gl.MeshData.sphere(20, 20, 1)

        # self.setMinimumSize(175, 131)
        self.setMinimumSize(800, 600)
        self.setWindowTitle(item.text())
        self.setWindowIcon(item.icon())
        self._set_draw_item()
        self.draw()

    def _set_draw_item(self):
        self.__molecule_index, self._draw_item = self.__atomic_coordinates_item(self.__molecule_index, self.item)

    def _build_molecule(self) -> Optional[MoleculeStruct]:
        """
        Builds molecule graphics object from `AtomicCoordinates` data structure
        """
        if not self._draw_item:
            return None

        ds: AtomicCoordinatesDS = self._draw_item.data()
        distance = 0
        atoms = []
        pos = Vector(np.sum(ds.x) / ds.x.size, np.sum(ds.y) / ds.y.size, np.sum(ds.z) / ds.z.size)
        for i, atomic_num in enumerate(ds.atomic_num):
            mesh_item = gl.GLMeshItem(
                meshdata=self.__sphere_mesh_data,
                smooth=True,
                shader="shaded",
                color=self.normalize_color(COLOR[atomic_num]),
            )
            mesh_item.scale(AT_RAD[atomic_num], AT_RAD[atomic_num], AT_RAD[atomic_num])
            mesh_item.translate(ds.x[i], ds.y[i], ds.z[i])
            atoms.append(mesh_item)

            d = (
                math.sqrt(((ds.x[i] - pos.x()) ** 2 + (ds.y[i] - pos.y()) ** 2 + (ds.z[i] - pos.z()) ** 2))
                + AT_RAD[atomic_num]
            )
            if d > distance:
                distance = d

        bonds = []
        geom_bond_tol = 0.15
        for i in range(len(ds.atomic_num)):
            crad_i = AT_SBCOVRAD[ds.atomic_num[i]]
            for j in range(i):
                crad_j = AT_SBCOVRAD[ds.atomic_num[j]]
                crad_sum = crad_i + crad_j
                dist_ij = math.sqrt((ds.x[i] - ds.x[j]) ** 2 + (ds.y[i] - ds.y[j]) ** 2 + (ds.z[i] - ds.z[j]) ** 2)
                if dist_ij < (crad_sum + crad_sum * geom_bond_tol):
                    bonds.append((i, j))

        return MoleculeStruct(atoms, pos, distance * 2.6)

    def draw(self):
        """
        Sets graphics objects to draw and camera position
        """
        self.clear()
        if molecule := self._build_molecule():
            for atom in molecule.atoms:
                self.addItem(atom)
            if not self.__camera_set:
                self.setCameraPosition(pos=molecule.center, distance=molecule.radius)
                self.__camera_set = True

    def normalize_color(self, value: int) -> Tuple[float, float, float, float]:
        """
        Converts 24 bit integer to tuple, where each component represented from 0.0 to 1.0
        """
        return ((value >> 16) / 255, ((value & 0xFF00) >> 8) / 255, (value & 0xFF) / 255, 1.0)

    def __atomic_coordinates_item(self, index: int, parent: "Item", counter: int = -1) -> Tuple[int, Optional["Item"]]:
        """
        Finds item with `AtomicCoordinates` data structure
        """
        index = max(0, index)
        last_item = None
        for i in range(parent.rowCount()):
            item = parent.child(i)
            if isinstance(item.data(), AtomicCoordinatesDS):
                last_item = item
                counter += 1
                if index == counter:
                    return counter, item
            elif item.hasChildren():
                return self.__atomic_coordinates_item(index, item, counter)
        return counter, last_item

    def _key_press_handler(self, event: QKeyEvent) -> bool:
        """
        :return: Has the event been processed
        """
        ctrl_left = {
            QKeyCombination(Qt.ControlModifier | Qt.KeypadModifier, Qt.Key_Left),
            QKeyCombination(Qt.ControlModifier, Qt.Key_Left),
        }
        ctrl_right = {
            QKeyCombination(Qt.ControlModifier | Qt.KeypadModifier, Qt.Key_Right),
            QKeyCombination(Qt.ControlModifier, Qt.Key_Right),
        }
        if event.keyCombination() in ctrl_left:
            # Ctrl + Left
            if self.__molecule_index > 0:
                self.__molecule_index -= 1
                self._set_draw_item()
                self.draw()
        elif event.keyCombination() in ctrl_right:
            # Ctrl + Right
            self.__molecule_index += 1
            item = self._draw_item
            self._set_draw_item()
            if id(item) != id(self._draw_item):
                self.draw()
        else:
            # No match
            return False  # not processed
        return True  # processed

    def keyPressEvent(self, event: QKeyEvent):
        if not self._key_press_handler(event):
            super().keyPressEvent(event)
