import math
from typing import TYPE_CHECKING, Optional

import numpy as np
from PySide6.QtCore import Slot
from PySide6.QtGui import QContextMenuEvent, QSurfaceFormat, QVector3D
from PySide6.QtWidgets import QMessageBox, QWidget

from mir_commander.consts import ATOM_SINGLE_BOND_COVALENT_RADIUS
from mir_commander.data_structures.molecule import AtomicCoordinates as AtomicCoordinatesDS
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.save_image_dialog import SaveImageDialog
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.scene import Scene
from mir_commander.ui.main_window.widgets.viewers.molecular_structure.style import Style
from mir_commander.ui.utils.opengl.keymap import Keymap
from mir_commander.ui.utils.opengl.widget import Widget
from mir_commander.ui.utils.widget import Action, Menu, StatusBar

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow
    from mir_commander.ui.utils.item import Item


class MolecularStructure(Widget):
    def __init__(self, parent: QWidget, item: "Item", main_window: "MainWindow", all: bool = False):
        self._main_window = main_window
        self._config = main_window.project.config.nested("widgets.viewers.molecular_structure")

        project_id = id(main_window.project)
        self._style = Style(project_id, self._config)
        keymap = Keymap(project_id, self._config["keymap"])

        super().__init__(scene=Scene(self, self._style), keymap=keymap, parent=parent)

        self._scene: Scene

        self.setMinimumSize(self._config["min_size"][0], self._config["min_size"][1])
        self.resize(self._config["size"][0], self._config["size"][1])

        self.item = item
        self.all = all

        self._keymap.load_from_config(self._config["keymap"])

        if self._config["antialiasing"]:
            sf = QSurfaceFormat()
            sf.setSamples(16)
            self.setFormat(sf)

        self._molecule_index = 0
        self._draw_item = None
        self._set_draw_item()

        # Menus and actions specific for this particular widget
        self.context_menu = Menu("", self)
        save_img_action = Action(Action.tr("Save image..."), self)
        self.context_menu.addAction(save_img_action)

        # Connect the actions to methods
        save_img_action.triggered.connect(self.save_img_action_handler)

        self.update_window_title()

        self._build_molecule()

    def _init_actions(self):
        super()._init_actions()
        self._actions["item_next"] = (False, self._draw_next_item, tuple())
        self._actions["item_prev"] = (False, self._draw_prev_item, tuple())
        self._actions["style_next"] = (False, self._set_next_style, tuple())
        self._actions["style_prev"] = (False, self._set_prev_style, tuple())
        self._actions["save_image"] = (False, self.save_img_action_handler, tuple())
        self._actions["toggle_atom_selection"] = (False, self._scene.toggle_atom_selection, tuple())

    def _apply_style(self):
        self._scene.apply_style()

    def _atomic_coordinates_item(
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

        ds: AtomicCoordinatesDS = self._draw_item.data()

        longest_distance = 0

        # add atoms
        for i, atomic_num in enumerate(ds.atomic_num):
            position = QVector3D(ds.x[i], ds.y[i], ds.z[i])
            atom = self._scene.add_atom(atomic_num, position)

            d = position.length() + atom.radius
            if longest_distance < d:
                longest_distance = d

        # add bonds
        self._build_bonds(ds)

        center = QVector3D(np.sum(ds.x) / ds.x.size, np.sum(ds.y) / ds.y.size, np.sum(ds.z) / ds.z.size)
        self._scene.set_center(center)
        self._scene.set_camera_distance(longest_distance - center.length())

    def _build_bonds(self, ds: AtomicCoordinatesDS):
        geom_bond_tol = 0.15
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
                    self._scene.add_bond(self._scene.atom(i), self._scene.atom(j))

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
            self._scene.clear(update=False)
            self._build_molecule()
            self.update()

    def _draw_next_item(self):
        self._molecule_index += 1
        item = self._draw_item
        self._set_draw_item()
        if id(item) != id(self._draw_item):
            self.update_window_title()
            self._scene.clear(update=False)
            self._build_molecule()
            self.update()

    def contextMenuEvent(self, event: QContextMenuEvent):
        # Show the context menu
        self.context_menu.exec(event.globalPos())

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
                image = self._scene.render_to_image(dlg.img_width, dlg.img_height, dlg.transparent_bg)
                image.save(str(dlg.img_file_path))
                self._main_window.status.showMessage(StatusBar.tr("Image saved"), 10000)

    def update_window_title(self):
        title = self._draw_item.text()
        parent_item = self._draw_item.parent()
        while parent_item:
            title = parent_item.text() + "/" + title
            parent_item = parent_item.parent()
        self.setWindowTitle(title)
        self.setWindowIcon(self._draw_item.icon())
