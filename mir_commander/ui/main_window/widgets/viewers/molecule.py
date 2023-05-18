import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph import Transform3D, Vector
from PySide6.QtCore import QCoreApplication, QKeyCombination, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QQuaternion, QSurfaceFormat

from mir_commander.data_structures.molecule import AtomicCoordinates as AtomicCoordinatesDS

if TYPE_CHECKING:
    from mir_commander.utils.item import Item


ATOM_SINGLE_BOND_COVALENT_RADIUS = [
    0.50,
    0.32,
    0.46,
    1.33,
    1.02,
    0.85,
    0.75,
    0.71,
    0.63,
    0.64,
    0.67,
    1.55,
    1.39,
    1.26,
    1.16,
    1.11,
    1.03,
    0.99,
    0.96,
    1.96,
    1.71,
    1.48,
    1.36,
    1.34,
    1.22,
    1.19,
    1.16,
    1.11,
    1.10,
    1.12,
    1.18,
    1.24,
    1.21,
    1.21,
    1.16,
    1.14,
    1.17,
    2.10,
    1.85,
    1.63,
    1.54,
    1.47,
    1.38,
    1.28,
    1.25,
    1.25,
    1.20,
    1.28,
    1.36,
    1.42,
    1.40,
    1.40,
    1.36,
    1.33,
    1.31,
    2.32,
    1.96,
    1.80,
    1.63,
    1.76,
    1.74,
    1.73,
    1.72,
    1.68,
    1.69,
    1.68,
    1.67,
    1.66,
    1.65,
    1.64,
    1.70,
    1.62,
    1.52,
    1.46,
    1.37,
    1.31,
    1.29,
    1.22,
    1.23,
    1.24,
    1.33,
    1.44,
    1.44,
    1.51,
    1.45,
    1.47,
    1.42,
    2.23,
    2.01,
    1.86,
    1.75,
    1.69,
    1.70,
    1.71,
    1.72,
    1.66,
    1.66,
    1.68,
    1.68,
    1.65,
    1.67,
    1.73,
    1.76,
    1.61,
    1.57,
    1.49,
    1.43,
    1.41,
    1.34,
    1.29,
    1.28,
    1.21,
]

ATOM_RADIUS = [
    0.1,
    0.15,
    0.17,
    0.20,
    0.22,
    0.24,
    0.26,
    0.28,
    0.30,
    0.32,
    0.34,
    0.30,
    0.32,
    0.34,
    0.36,
    0.38,
    0.40,
    0.42,
    0.44,
    0.40,
    0.41,
    0.42,
    0.43,
    0.44,
    0.45,
    0.46,
    0.47,
    0.48,
    0.49,
    0.50,
    0.51,
    0.52,
    0.53,
    0.54,
    0.55,
    0.56,
    0.57,
    0.50,
    0.51,
    0.52,
    0.53,
    0.54,
    0.55,
    0.56,
    0.57,
    0.58,
    0.59,
    0.60,
    0.61,
    0.62,
    0.63,
    0.64,
    0.65,
    0.66,
    0.67,
    0.60,
    0.61,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.62,
    0.63,
    0.64,
    0.65,
    0.66,
    0.67,
    0.68,
    0.69,
    0.70,
    0.71,
    0.72,
    0.73,
    0.74,
    0.75,
    0.76,
    0.77,
    0.70,
    0.71,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.72,
    0.73,
    0.74,
    0.75,
    0.76,
    0.77,
    0.78,
    0.79,
    0.80,
    0.81,
    0.82,
    0.83,
    0.84,
    0.85,
    0.86,
    0.87,
]

ATOM_COLOR = [
    "#00FBFF",
    "#FFFFFF",
    "#D9FFFF",
    "#CC80FF",
    "#C2FF00",
    "#FFB5B5",
    "#909090",
    "#3050F8",
    "#FF0D0D",
    "#90E050",
    "#B3E3F5",
    "#AB5CF2",
    "#8AFF00",
    "#BFA6A6",
    "#F0C8A0",
    "#FF8000",
    "#FFFF30",
    "#1FF01F",
    "#80D1E3",
    "#8F40D4",
    "#3DFF00",
    "#E6E6E6",
    "#BFC2C7",
    "#A6A6AB",
    "#8A99C7",
    "#9C7AC7",
    "#E06633",
    "#F090A0",
    "#50D050",
    "#C88033",
    "#7D80B0",
    "#C28F8F",
    "#668F8F",
    "#BD80E3",
    "#FFA100",
    "#A62929",
    "#5CB8D1",
    "#702EB0",
    "#00FF00",
    "#94FFFF",
    "#94E0E0",
    "#73C2C9",
    "#54B5B5",
    "#3B9E9E",
    "#248F8F",
    "#0A7D8C",
    "#006985",
    "#C0C0C0",
    "#FFD98F",
    "#A67573",
    "#668080",
    "#9E63B5",
    "#D47A00",
    "#940094",
    "#429EB0",
    "#57178F",
    "#00C900",
    "#70D4FF",
    "#FFFFC7",
    "#D9FFC7",
    "#C7FFC7",
    "#A3FFC7",
    "#8FFFC7",
    "#61FFC7",
    "#45FFC7",
    "#30FFC7",
    "#1FFFC7",
    "#00FF9C",
    "#00E675",
    "#00D452",
    "#00BF38",
    "#00AB24",
    "#4DC2FF",
    "#4DA6FF",
    "#2194D6",
    "#267DAB",
    "#266696",
    "#175487",
    "#D0D0E0",
    "#FFD123",
    "#B8B8D0",
    "#A6544D",
    "#575961",
    "#9E4FB5",
    "#AB5C00",
    "#754F45",
    "#428296",
    "#420066",
    "#007D00",
    "#70ABFA",
    "#00BAFF",
    "#00A1FF",
    "#008FFF",
    "#0080FF",
    "#006BFF",
    "#545CF2",
    "#785CE3",
    "#8A4FE3",
    "#A136D4",
    "#B31FD4",
    "#B31FBA",
    "#B30DA6",
    "#BD0D87",
    "#C70066",
    "#CC0059",
    "#D1004F",
    "#D90045",
    "#E00038",
    "#E6002E",
    "#EB0026",
    "#F00024",
    "#F00024",
    "#F00024",
    "#F00024",
    "#F00024",
    "#F00024",
    "#F00024",
    "#F00024",
    "#F00024",
]


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

        mesh_quality = self._config.get("quality.mesh", 0.5)
        mesh_quality = max(min(mesh_quality, 1), 0.1)
        mesh_quality = int(mesh_quality * 50)
        bond_radius = self._config.get("bond.radius", 0.07)
        self.__atom_mesh_data = gl.MeshData.sphere(mesh_quality, mesh_quality, radius=1)
        self.__bond_mesh_data = gl.MeshData.cylinder(1, mesh_quality, [bond_radius, bond_radius], length=1)

        self.__at_rad = self._config["atoms.radius"]
        if not self.__at_rad or len(self.__at_rad) != 119:
            self.__at_rad = ATOM_RADIUS

        self.__at_color = self._config["atoms.color"]
        if not self.__at_color or len(self.__at_color) != 119:
            self.__at_color = ATOM_COLOR

        self.__at_sbcovrad = self._global_config["atom_single_bond_covalent_radius"]
        if not self.__at_sbcovrad or len(self.__at_color) != 119:
            self.__at_sbcovrad = ATOM_SINGLE_BOND_COVALENT_RADIUS

        if self._config.get("quality.antialiasing", False):
            sf = QSurfaceFormat()
            sf.setSamples(16)
            self.setFormat(sf)

        self.setMinimumSize(200, 150)
        self.setWindowTitle(item.text())
        self.setWindowIcon(item.icon())
        self.setBackgroundColor(self._config.get("background.color", "#000000"))
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
                meshdata=self.__atom_mesh_data,
                smooth=self._config.get("quality.smooth", True),
                shader="shaded",
                color=self.normalize_color(self.__at_color[atomic_num]),
            )
            mesh_item.scale(self.__at_rad[atomic_num], self.__at_rad[atomic_num], self.__at_rad[atomic_num])
            mesh_item.translate(ds.x[i], ds.y[i], ds.z[i])
            atoms.append(mesh_item)

            d = (
                math.sqrt(((ds.x[i] - pos.x()) ** 2 + (ds.y[i] - pos.y()) ** 2 + (ds.z[i] - pos.z()) ** 2))
                + self.__at_rad[atomic_num]
            )
            if d > distance:
                distance = d

        bonds = []
        geom_bond_tol = 0.15
        for i in range(len(ds.atomic_num)):
            crad_i = self.__at_sbcovrad[ds.atomic_num[i]]
            for j in range(i):
                crad_j = self.__at_sbcovrad[ds.atomic_num[j]]
                crad_sum = crad_i + crad_j
                dist_ij = math.sqrt((ds.x[i] - ds.x[j]) ** 2 + (ds.y[i] - ds.y[j]) ** 2 + (ds.z[i] - ds.z[j]) ** 2)
                if dist_ij < (crad_sum + crad_sum * geom_bond_tol):
                    mesh_item = gl.GLMeshItem(
                        meshdata=self.__bond_mesh_data,
                        smooth=self._config.get("quality.smooth", True),
                        shader="shaded",
                        color=self.normalize_color(self._config.get("bond.color", "#888888")),
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

        return MoleculeStruct(atoms, bonds, pos, distance * 2.6)

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
