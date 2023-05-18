import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph import Transform3D, Vector
from PySide6.QtCore import QCoreApplication, QKeyCombination, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QQuaternion, QSurfaceFormat

from mir_commander.const import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.data_structures.molecule import AtomicCoordinates as AtomicCoordinatesDS

if TYPE_CHECKING:
    from mir_commander.utils.item import Item


@dataclass
class MoleculeStruct:
    atoms: List[gl.GLMeshItem]
    bonds: List[gl.GLMeshItem]
    center: Vector
    radius: float


class Molecule(gl.GLViewWidget):
    def __init__(self, item: "Item"):
        super().__init__(None, rotationMethod="quaternion")
        self.item = item
        self._global_config = QCoreApplication.instance().config
        self._config = self._global_config.nested("widgets.viewers.molecule")
        self._draw_item = None
        self.__molecule_index = 0
        self.__camera_set = False
        self.__mouse_pos = None

        mesh_quality = self._config["quality.mesh"]
        mesh_quality = max(min(mesh_quality, 1), 0.1)
        mesh_quality = int(mesh_quality * 50)
        bond_radius = self._config["bond.radius"]
        self.__atom_mesh_data = gl.MeshData.sphere(mesh_quality, mesh_quality, radius=1)
        self.__bond_mesh_data = gl.MeshData.cylinder(1, mesh_quality, [bond_radius, bond_radius], length=1)

        self.__at_rad = self._config["atoms.radius"]
        self.__at_color = self._config["atoms.color"]

        if self._config["quality.antialiasing"]:
            sf = QSurfaceFormat()
            sf.setSamples(16)
            self.setFormat(sf)

        self.setMinimumSize(200, 150)
        self.setWindowTitle(item.text())
        self.setWindowIcon(item.icon())
        self.setBackgroundColor(self._config["background.color"])
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
        center = Vector(np.sum(ds.x) / ds.x.size, np.sum(ds.y) / ds.y.size, np.sum(ds.z) / ds.z.size)
        for i, atomic_num in enumerate(ds.atomic_num):
            mesh_item = gl.GLMeshItem(
                meshdata=self.__atom_mesh_data,
                smooth=self._config["quality.smooth"],
                shader="shaded",
                color=self.normalize_color(self.__at_color[atomic_num]),
            )
            radius = self._config["atoms.scale_factor"] * self.__at_rad[atomic_num]
            mesh_item.scale(radius, radius, radius)
            mesh_item.translate(ds.x[i], ds.y[i], ds.z[i])
            atoms.append(mesh_item)

            d = (
                math.sqrt(((ds.x[i] - center.x()) ** 2 + (ds.y[i] - center.y()) ** 2 + (ds.z[i] - center.z()) ** 2))
                + self.__at_rad[atomic_num]
            )
            if d > distance:
                distance = d

        bonds = []
        geom_bond_tol = 0.15
        for i in range(len(ds.atomic_num)):
            crad_i = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[i]]
            for j in range(i):
                crad_j = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[j]]
                crad_sum = crad_i + crad_j
                dist_ij = math.sqrt((ds.x[i] - ds.x[j]) ** 2 + (ds.y[i] - ds.y[j]) ** 2 + (ds.z[i] - ds.z[j]) ** 2)
                if dist_ij < (crad_sum + crad_sum * geom_bond_tol):
                    mesh_item = gl.GLMeshItem(
                        meshdata=self.__bond_mesh_data,
                        smooth=self._config["quality.smooth"],
                        shader="shaded",
                        color=self.normalize_color(self._config["bond.color"]),
                    )
                    tr = Transform3D()
                    tr.translate((ds.x[i] + ds.x[j]) / 2, (ds.y[i] + ds.y[j]) / 2, (ds.z[i] + ds.z[j]) / 2)
                    q = QQuaternion.rotationTo(
                        Vector(0, 0, 1), Vector(ds.x[i] - ds.x[j], ds.y[i] - ds.y[j], ds.z[i] - ds.z[j])
                    )
                    tr.rotate(q)
                    tr.scale(1, 1, dist_ij)
                    tr.translate(0, 0, -0.5)

                    mesh_item.applyTransform(tr, False)
                    bonds.append(mesh_item)

        return MoleculeStruct(atoms, bonds, center, distance * 2.6)

    def draw(self):
        """
        Sets graphics objects to draw and camera position
        """
        self.clear()
        if molecule := self._build_molecule():
            for atom in molecule.atoms + molecule.bonds:
                self.addItem(atom)
            for bond in molecule.bonds:
                self.addItem(bond)
            if not self.__camera_set:
                self.setCameraPosition(pos=molecule.center, distance=molecule.radius)
                self.__camera_set = True

    def normalize_color(self, value: str) -> Tuple[float, float, float, float]:
        """
        Converts #RRGGBB string to tuple, where each component represented from 0.0 to 1.0
        """
        return int(value[1:3], 16) / 255, int(value[3:5], 16) / 255, int(value[5:7], 16) / 255, 1.0

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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.__mouse_pos = event.position()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.position() - self.__mouse_pos
            self.__mouse_pos = event.position()
            self.orbit(-diff.x(), diff.y())
