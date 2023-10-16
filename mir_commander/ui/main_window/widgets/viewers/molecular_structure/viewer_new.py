import math
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QCoreApplication, QKeyCombination, Qt
from PySide6.QtGui import QKeyEvent, QVector3D
from PySide6.QtWidgets import QWidget

from mir_commander.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.data_structures.molecule import AtomicCoordinates as AtomicCoordinatesDS
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.scene import Scene
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.style import Style
from mir_commander.ui.utils.opengl.widget import Widget
from mir_commander.utils.config import Config

if TYPE_CHECKING:
    from mir_commander.ui.utils.item import Item


class MolecularStructureNew(Widget):
    styles: list[Config] = []

    def __init__(self, parent: QWidget, item: "Item", all: bool = False):
        super().__init__(parent)

        self.item = item
        self.all = all

        self.__style = Style.style("")

        global_config = QCoreApplication.instance().config
        config = global_config.nested("widgets.viewers.molecular_structure")
        self.setMinimumSize(config["min_size"][0], config["min_size"][1])
        self.resize(config["size"][0], config["size"][1])

        self.__molecule_index = 0
        self._draw_item = None
        self._set_draw_item()

        self.update_window_title()

        self._scene: Scene = Scene(self, self.__style)
        self._build_molecule()

    def __atomic_coordinates_item(
        self, index: int, parent: "Item", counter: int = -1
    ) -> tuple[bool, int, Optional["Item"]]:
        """
        Finds item with `AtomicCoordinates` data structure
        """
        index = max(0, index)
        last_item = None
        if not parent.hasChildren() and isinstance(parent.data(), AtomicCoordinatesDS):
            return True, 0, parent
        else:
            for i in range(parent.rowCount()):
                item = parent.child(i)
                if isinstance(item.data(), AtomicCoordinatesDS):
                    last_item = item
                    counter += 1
                    if index == counter:
                        return True, counter, item
                elif self.all and item.hasChildren():
                    found, counter, item = self.__atomic_coordinates_item(index, item, counter)
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

        ds: AtomicCoordinatesDS = self._draw_item.data()

        # add atoms
        for i, atomic_num in enumerate(ds.atomic_num):
            self._scene.add_atom(atomic_num, QVector3D(ds.x[i], ds.y[i], ds.z[i]))

        # add bonds
        self._build_bonds(ds)

    def _build_bonds(self, ds: AtomicCoordinatesDS):
        geom_bond_tol = 0.15
        for i in range(len(ds.atomic_num)):
            crad_i = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[i]]
            for j in range(i):
                crad_j = ATOM_SINGLE_BOND_COVALENT_RADIUS[ds.atomic_num[j]]
                crad_sum = crad_i + crad_j
                dist_ij = math.sqrt((ds.x[i] - ds.x[j]) ** 2 + (ds.y[i] - ds.y[j]) ** 2 + (ds.z[i] - ds.z[j]) ** 2)
                if dist_ij < (crad_sum + crad_sum * geom_bond_tol):
                    self._scene.add_bond(self._scene.atom(i), self._scene.atom(j))

    def _set_draw_item(self):
        _, self.__molecule_index, self._draw_item = self.__atomic_coordinates_item(self.__molecule_index, self.item)

    def _set_prev_style(self):
        if self.__style.set_prev_style():
            self._scene.apply_style()

    def _set_next_style(self):
        if self.__style.set_next_style():
            self._scene.apply_style()

    def _draw_prev_item(self):
        if self.__molecule_index > 0:
            self.__molecule_index -= 1
            self._set_draw_item()
            self.update_window_title()
            # self.draw()

    def _draw_next_item(self):
        self.__molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if id(item) != id(self._draw_item):
            self.update_window_title()
            # self.draw()

    def keyPressEvent(self, event: QKeyEvent):
        if not self._key_press_handler(event):
            super().keyPressEvent(event)

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

    def update_window_title(self):
        title = self._draw_item.text()
        parent_item = self._draw_item.parent()
        while parent_item:
            title = parent_item.text() + "/" + title
            parent_item = parent_item.parent()
        self.setWindowTitle(title)
        self.setWindowIcon(self._draw_item.icon())
