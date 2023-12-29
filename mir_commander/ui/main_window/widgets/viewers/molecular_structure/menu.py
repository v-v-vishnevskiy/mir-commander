from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon, QKeySequence
from PySide6.QtWidgets import QWidget

from mir_commander.ui.main_window.widgets.viewers.molecular_structure.viewer import MolecularStructure
from mir_commander.ui.utils.sub_window_menu import SubWindowMenu
from mir_commander.ui.utils.widget import Action, Menu

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class MolStructMenu(SubWindowMenu):
    widget: QWidget = MolecularStructure

    def __init__(self, parent: "MainWindow"):
        super().__init__(Menu.tr("&Molecule"), parent)
        self.setObjectName("Molecular Structure Menu")

        selection_menu = Menu(Menu.tr("Selection"))
        self.addMenu(selection_menu)

        select_all_atoms_act = Action(Action.tr("Select all atoms"), self.parent())
        select_all_atoms_act.triggered.connect(self.select_all_atoms_handler)
        selection_menu.addAction(select_all_atoms_act)

        unselect_all_atoms_act = Action(Action.tr("Unselect all atoms"), self.parent())
        unselect_all_atoms_act.triggered.connect(self.unselect_all_atoms_handler)
        selection_menu.addAction(unselect_all_atoms_act)

        calc_menu = Menu(Menu.tr("Calculate"))
        self.addMenu(calc_menu)

        calc_interat_distance_act = Action(Action.tr("Interatomic distance"), self.parent())
        calc_interat_distance_act.triggered.connect(self.calc_interat_distance_handler)
        calc_menu.addAction(calc_interat_distance_act)

        calc_interat_angle_act = Action(Action.tr("Interatomic angle"), self.parent())
        calc_interat_angle_act.triggered.connect(self.calc_interat_angle_handler)
        calc_menu.addAction(calc_interat_angle_act)

        cloaking_menu = Menu(Menu.tr("Cloaking"))
        self.addMenu(cloaking_menu)

        cloak_selected_act = Action(Action.tr("Cloak selected"), self.parent())
        cloak_selected_act.triggered.connect(self.cloak_selected_handler)
        cloaking_menu.addAction(cloak_selected_act)

        cloak_not_selected_act = Action(Action.tr("Cloak not selected"), self.parent())
        cloak_not_selected_act.triggered.connect(self.cloak_not_selected_handler)
        cloaking_menu.addAction(cloak_not_selected_act)

        cloak_h_atoms_act = Action(Action.tr("Cloak H atoms"), self.parent())
        cloak_h_atoms_act.triggered.connect(self.cloak_h_atoms_handler)
        cloaking_menu.addAction(cloak_h_atoms_act)

        toggle_h_atoms_act = Action(Action.tr("Toggle H atoms"), self.parent())
        toggle_h_atoms_act.setShortcut(QKeySequence("Ctrl+H"))
        toggle_h_atoms_act.triggered.connect(self.toggle_h_atoms_handler)
        cloaking_menu.addAction(toggle_h_atoms_act)

        cloak_at_by_type_act = Action(Action.tr("Cloak atoms by type..."), self.parent())
        cloak_at_by_type_act.triggered.connect(self.cloak_atoms_by_type_handler)
        cloaking_menu.addAction(cloak_at_by_type_act)

        cloaking_menu.addSeparator()

        uncloak_all_act = Action(Action.tr("Uncloak all"), self.parent())
        uncloak_all_act.triggered.connect(self.uncloak_all_handler)
        cloaking_menu.addAction(uncloak_all_act)

        save_img_act = Action(Action.tr("Save image..."), self.parent())
        save_img_act.setIcon(QIcon(":/icons/actions/saveimage.png"))
        save_img_act.triggered.connect(self.save_img_action_handler)
        self.addAction(save_img_act)

        self.set_enabled(False)

    # Note, callbacks are only triggered, when the respective action is enabled.
    # Whether this is the case, is determined by the update_state method of the SubWindowMenu class.
    # This method receives the window parameter, so it is possible to determine the currently active type
    # of widget. Thus, it is guaranteed that mdi_area.activeSubWindow() is actually a MolViewer instance
    # and we may call our respective action handler.

    @Slot()
    def select_all_atoms_handler(self):
        self.mdi_area.activeSubWindow().widget()._scene.select_all_atoms()

    @Slot()
    def unselect_all_atoms_handler(self):
        self.mdi_area.activeSubWindow().widget()._scene.unselect_all_atoms()

    @Slot()
    def calc_interat_distance_handler(self):
        self.mdi_area.activeSubWindow().widget().calc_distance_last2sel_atoms()

    @Slot()
    def calc_interat_angle_handler(self):
        self.mdi_area.activeSubWindow().widget().calc_angle_last3sel_atoms()

    @Slot()
    def save_img_action_handler(self):
        self.mdi_area.activeSubWindow().widget().save_img_action_handler()

    @Slot()
    def cloak_selected_handler(self):
        self.mdi_area.activeSubWindow().widget()._scene.cloak_selected_atoms()

    @Slot()
    def cloak_not_selected_handler(self):
        self.mdi_area.activeSubWindow().widget()._scene.cloak_not_selected_atoms()

    @Slot()
    def cloak_h_atoms_handler(self):
        self.mdi_area.activeSubWindow().widget()._scene.cloak_h_atoms()

    @Slot()
    def toggle_h_atoms_handler(self):
        self.mdi_area.activeSubWindow().widget()._scene.toggle_h_atoms()

    @Slot()
    def cloak_atoms_by_type_handler(self):
        self.mdi_area.activeSubWindow().widget().cloak_atoms_by_atnum()

    @Slot()
    def uncloak_all_handler(self):
        self.mdi_area.activeSubWindow().widget()._scene.uncloak_all_atoms()
