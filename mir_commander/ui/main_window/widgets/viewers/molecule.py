import logging
import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

import numpy as np
import pyqtgraph.opengl as gl
from pyqtgraph import Transform3D, Vector
from PySide6.QtCore import QCoreApplication, QKeyCombination, Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent, QQuaternion, QSurfaceFormat

from mir_commander.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS, DIR
from mir_commander.data_structures.molecule import AtomicCoordinates as AtomicCoordinatesDS
from mir_commander.utils.config import Config

if TYPE_CHECKING:
    from mir_commander.utils.item import Item


logger = logging.getLogger(__name__)


@dataclass
class MoleculeStruct:
    atoms: List[gl.GLMeshItem]
    bonds: List[gl.GLMeshItem]


class Molecule(gl.GLViewWidget):
    styles: List[Config] = []

    def __init__(self, item: "Item"):
        super().__init__(None, rotationMethod="quaternion")
        self.item = item
        self._global_config = QCoreApplication.instance().config
        self._config = self._global_config.nested("widgets.viewers.molecule")
        self._draw_item = None
        self.__molecule_index = 0
        self.__default_style = self._config.nested("style.default")
        self.__camera_set = False
        self.__mouse_pos = None
        self.__atom_mesh_data = None
        self.__bond_mesh_data = None
        self.__at_rad: List[int] = []
        self.__at_color: List[str] = []

        if not self.styles:
            self._load_styles()

        self.__style = self.styles[0]
        self._set_style(self._config["style.current"])
        self.__apply_style()

        if self._config["antialiasing"]:
            sf = QSurfaceFormat()
            sf.setSamples(16)
            self.setFormat(sf)

        self.setMinimumSize(200, 150)
        self.setWindowTitle(item.text())
        self.setWindowIcon(item.icon())
        self._set_draw_item()
        self.draw()

    def _load_styles(self):
        styles = [self.__default_style]
        for file in (DIR.CONFIG / "styles" / "viewers" / "molecule").glob("*.yaml"):
            style = Config(file)
            style.set_defaults(self.__default_style)
            styles.append(style)
        self.__class__.styles = sorted(styles, key=lambda x: x["name"])

    def _set_draw_item(self):
        self.__molecule_index, self._draw_item = self.__atomic_coordinates_item(self.__molecule_index, self.item)

    def _set_style(self, name: str):
        for style in self.styles:
            if style["name"] == name:
                self.__style = style
                break
        else:
            self.__style = self.__default_style

    def __apply_style(self):
        mesh_quality = self.__style["quality.mesh"]
        mesh_quality = max(min(mesh_quality, 1), 0.1)
        mesh_quality = int(mesh_quality * 50)
        bond_radius = self.__style["bond.radius"]
        self.__atom_mesh_data = gl.MeshData.sphere(mesh_quality, mesh_quality, radius=1)
        self.__bond_mesh_data = gl.MeshData.cylinder(1, mesh_quality, [bond_radius, bond_radius], length=1)

        self.__at_rad = self.__style["atoms.radius"]
        self.__at_color = self.__style["atoms.color"]

    def _build_molecule(self) -> Optional[MoleculeStruct]:
        """
        Builds molecule graphics object from `AtomicCoordinates` data structure
        """
        if not self._draw_item:
            return None

        ds: AtomicCoordinatesDS = self._draw_item.data()
        atoms = self._build_atoms(ds)
        bonds = self._build_bonds(ds)

        return MoleculeStruct(atoms, bonds)

    def _build_atoms(self, ds: AtomicCoordinatesDS) -> List[gl.GLMeshItem]:
        result = []
        for i, atomic_num in enumerate(ds.atomic_num):
            mesh_item = gl.GLMeshItem(
                meshdata=self.__atom_mesh_data,
                smooth=self.__style["quality.smooth"],
                shader="shaded",
                color=self.normalize_color(self.__at_color[atomic_num]),
            )
            if self.__style["atoms.enabled"]:
                radius = self.__style["atoms.scale_factor"] * self.__at_rad[atomic_num]
            else:
                radius = self.__style["bond.radius"]
            mesh_item.scale(radius, radius, radius)
            mesh_item.translate(ds.x[i], ds.y[i], ds.z[i])
            result.append(mesh_item)
        return result

    def _build_bonds(self, ds: AtomicCoordinatesDS) -> List[gl.GLMeshItem]:
        result = []
        geom_bond_tol = 0.15
        for i in range(len(ds.atomic_num)):
            crad_i = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[i]]
            for j in range(i):
                crad_j = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[j]]
                crad_sum = crad_i + crad_j
                dist_ij = math.sqrt((ds.x[i] - ds.x[j]) ** 2 + (ds.y[i] - ds.y[j]) ** 2 + (ds.z[i] - ds.z[j]) ** 2)
                if dist_ij < (crad_sum + crad_sum * geom_bond_tol):
                    result.extend(
                        self._build_bond(
                            dist_ij,
                            Vector(ds.x[i], ds.y[i], ds.z[i]),
                            Vector(ds.x[j], ds.y[j], ds.z[j]),
                            ds.atomic_num[i],
                            ds.atomic_num[j],
                        )
                    )
        return result

    def _build_bond(self, length: float, atom1: Vector, atom2: Vector, a_num1: int, a_num2: int) -> List[gl.GLMeshItem]:
        result = []
        color = self.__style["bond.color"]
        if color.startswith("#") and len(color) == 7:
            result.append(self.__build_cylinder(length, atom1, atom2, color))
        elif self.__style["bond.color"] == "atoms":
            if a_num1 == a_num2:
                result.append(self.__build_cylinder(length, atom1, atom2, self.__at_color[a_num1]))
            else:
                if self.__style["atoms.enabled"]:
                    rad1 = self.__at_rad[a_num1] * self.__style["atoms.scale_factor"]
                    rad2 = self.__at_rad[a_num2] * self.__style["atoms.scale_factor"]
                    mid_length = length - rad1 - rad2
                    if mid_length > 0:
                        length1 = rad1 + mid_length / 2
                        length2 = rad2 + mid_length / 2
                        mid = atom2 - atom1
                        mid.normalize()
                        mid = (mid * length1) + atom1
                        result.append(self.__build_cylinder(length1, atom1, mid, self.__at_color[a_num1]))
                        result.append(self.__build_cylinder(length2, mid, atom2, self.__at_color[a_num2]))
                else:
                    mid = (atom1 + atom2) / 2
                    result.append(self.__build_cylinder(length / 2, atom1, mid, self.__at_color[a_num1]))
                    result.append(self.__build_cylinder(length / 2, mid, atom2, self.__at_color[a_num2]))
        else:
            logger.warning("Parameter `bond.color` is not set. Use default color #888888")
            result.append(self.__build_cylinder(length, atom1, atom2, "#888888"))
        return result

    def __build_cylinder(self, length: float, start: Vector, end: Vector, color: str) -> gl.GLMeshItem:
        mesh_item = gl.GLMeshItem(
            meshdata=self.__bond_mesh_data,
            smooth=self.__style["quality.smooth"],
            shader="shaded",
            color=self.normalize_color(color),
        )
        tr = Transform3D()
        tr.translate((start + end) / 2)
        tr.rotate(QQuaternion.rotationTo(Vector(0, 0, 1), start - end))
        tr.scale(1, 1, length)
        tr.translate(0, 0, -0.5)
        mesh_item.applyTransform(tr, False)
        return mesh_item

    def _set_camera_position(self):
        ds: AtomicCoordinatesDS = self._draw_item.data()
        center = Vector(np.sum(ds.x) / ds.x.size, np.sum(ds.y) / ds.y.size, np.sum(ds.z) / ds.z.size)
        distance = 0
        for i, atomic_num in enumerate(ds.atomic_num):
            d = (
                math.sqrt(((ds.x[i] - center.x()) ** 2 + (ds.y[i] - center.y()) ** 2 + (ds.z[i] - center.z()) ** 2))
                + self.__at_rad[atomic_num]
            )
            if d > distance:
                distance = d

        self.setCameraPosition(pos=center, distance=distance * 2.6)

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
                self._set_camera_position()
                self.__camera_set = True
        self.setBackgroundColor(self.__style["background.color"])

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
        ctrl_up = {
            QKeyCombination(Qt.ControlModifier | Qt.KeypadModifier, Qt.Key_Up),
            QKeyCombination(Qt.ControlModifier, Qt.Key_Up),
        }
        ctrl_down = {
            QKeyCombination(Qt.ControlModifier | Qt.KeypadModifier, Qt.Key_Down),
            QKeyCombination(Qt.ControlModifier, Qt.Key_Down),
        }
        if event.keyCombination() in ctrl_left:  # Ctrl + Left
            self._draw_prev_item()
        elif event.keyCombination() in ctrl_right:  # Ctrl + Right
            self._draw_next_item()
        elif event.keyCombination() in ctrl_up:  # Ctrl + Up
            self._set_prev_style()
        elif event.keyCombination() in ctrl_down:  # Ctrl + Down
            self._set_next_style()
        else:
            # No match
            return False  # not processed
        return True  # processed

    def _draw_prev_item(self):
        if self.__molecule_index > 0:
            self.__molecule_index -= 1
            self._set_draw_item()
            self.draw()

    def _draw_next_item(self):
        self.__molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if id(item) != id(self._draw_item):
            self.draw()

    def _set_prev_style(self):
        current_style = self.__style
        prev_style = self.styles[0]
        for style in self.styles[1:]:
            if style["name"] == self.__style["name"]:
                self.__style = prev_style
                break
            else:
                prev_style = style
        if current_style["name"] != self.__style["name"]:
            self.__apply_style()
            self.draw()

    def _set_next_style(self):
        current_style = self.__style
        for i, style in enumerate(self.styles):
            if style["name"] == self.__style["name"]:
                self.__style = self.styles[min(i + 1, len(self.styles) - 1)]
                break
        if current_style["name"] != self.__style["name"]:
            self.__apply_style()
            self.draw()

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
