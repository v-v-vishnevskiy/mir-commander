from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon, QKeySequence

from mir_commander.ui.main_window.widgets.viewers.molecular_structure.viewer import MolecularStructure
from mir_commander.ui.utils.sub_window_menu import SubWindowMenu
from mir_commander.ui.utils.widget import Action
from mir_commander.ui.utils.widget import Menu as BaseMenu

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class Menu(SubWindowMenu[MolecularStructure]):
    def __init__(self, parent: "MainWindow"):
        super().__init__(Menu.tr("&Molecule"), parent)
        self.setObjectName("Molecular Structure Menu")

        self._init_selection_menu()
        self._init_calculate_menu()
        self._init_cloaking_menu()

        save_img_act = Action(Action.tr("Save image..."), self.parent())
        save_img_act.setIcon(QIcon(":/icons/actions/saveimage.png"))
        save_img_act.triggered.connect(self.save_img_action_handler)
        self.addAction(save_img_act)

        self.set_enabled_actions(False)

    def _init_selection_menu(self):
        selection_menu = BaseMenu(BaseMenu.tr("Selection"))
        self.addMenu(selection_menu)

        select_all_atoms_act = Action(Action.tr("Select all atoms"), self.parent())
        select_all_atoms_act.triggered.connect(self.select_all_atoms_handler)
        selection_menu.addAction(select_all_atoms_act)

        unselect_all_atoms_act = Action(Action.tr("Unselect all atoms"), self.parent())
        unselect_all_atoms_act.triggered.connect(self.unselect_all_atoms_handler)
        selection_menu.addAction(unselect_all_atoms_act)

        select_toggle_all_atoms_act = Action(Action.tr("Toggle all atoms"), self.parent())
        select_toggle_all_atoms_act.setShortcut(QKeySequence("A"))
        select_toggle_all_atoms_act.triggered.connect(self.select_toggle_all_atoms_handler)
        selection_menu.addAction(select_toggle_all_atoms_act)

    def _init_calculate_menu(self):
        calc_menu = BaseMenu(BaseMenu.tr("Calculate"))
        self.addMenu(calc_menu)

        calc_interat_distance_act = Action(Action.tr("Interatomic distance"), self.parent())
        calc_interat_distance_act.setStatusTip(Action.tr("Distance between last two selected atoms a1-a2"))
        calc_interat_distance_act.triggered.connect(self.calc_interat_distance_handler)
        calc_menu.addAction(calc_interat_distance_act)

        calc_interat_angle_act = Action(Action.tr("Interatomic angle"), self.parent())
        calc_interat_angle_act.setStatusTip(
            Action.tr("Angle between two lines formed by last three selected atoms a1-a2-a3")
        )
        calc_interat_angle_act.triggered.connect(self.calc_interat_angle_handler)
        calc_menu.addAction(calc_interat_angle_act)

        calc_torsion_angle_act = Action(Action.tr("Torsion angle"), self.parent())
        calc_torsion_angle_act.setStatusTip(
            Action.tr(
                "Dihedral angle between two planes (a1-a2-a3) and (a2-a3-a4) "
                "defined on the basis of last four selected atoms"
            )
        )
        calc_torsion_angle_act.triggered.connect(self.calc_torsion_angle_handler)
        calc_menu.addAction(calc_torsion_angle_act)

        calc_oop_angle_act = Action(Action.tr("Out-of-plane angle"), self.parent())
        calc_oop_angle_act.setStatusTip(
            Action.tr(
                "Angle between the vector (a1-a2) and plane (a3-a2-a4) defined on the basis of last four selected atoms"
            )
        )
        calc_oop_angle_act.triggered.connect(self.calc_oop_angle_handler)
        calc_menu.addAction(calc_oop_angle_act)

        calc_auto_parameter_act = Action(Action.tr("Auto parameter"), self.parent())
        calc_auto_parameter_act.setShortcut(QKeySequence("P"))
        calc_auto_parameter_act.setStatusTip(
            Action.tr("Interatomic distance, angle or torsion angle if two, three or four atoms are selected")
        )
        calc_auto_parameter_act.triggered.connect(self.calc_auto_parameter_handler)
        calc_menu.addAction(calc_auto_parameter_act)

        calc_sel_fragments_act = Action(Action.tr("Selected fragments"), self.parent())
        calc_sel_fragments_act.setStatusTip(
            Action.tr("Calculate all geometric parameters for fragments with selected atoms")
        )
        calc_sel_fragments_act.triggered.connect(self.calc_sel_fragments_handler)
        calc_menu.addAction(calc_sel_fragments_act)

    def _init_cloaking_menu(self):
        cloaking_menu = BaseMenu(BaseMenu.tr("Cloaking"))
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

        cloak_toggle_h_atoms_act = Action(Action.tr("Toggle H atoms"), self.parent())
        cloak_toggle_h_atoms_act.setShortcut(QKeySequence("H"))
        cloak_toggle_h_atoms_act.triggered.connect(self.cloak_toggle_h_atoms_handler)
        cloaking_menu.addAction(cloak_toggle_h_atoms_act)

        cloak_at_by_type_act = Action(Action.tr("Cloak atoms by type..."), self.parent())
        cloak_at_by_type_act.triggered.connect(self.cloak_atoms_by_type_handler)
        cloaking_menu.addAction(cloak_at_by_type_act)

        cloaking_menu.addSeparator()

        uncloak_all_act = Action(Action.tr("Uncloak all"), self.parent())
        uncloak_all_act.triggered.connect(self.uncloak_all_handler)
        cloaking_menu.addAction(uncloak_all_act)

    # Note, callbacks are only triggered, when the respective action is enabled.
    # Whether this is the case, is determined by the update_state method of the SubWindowMenu class.
    # This method receives the window parameter, so it is possible to determine the currently active type
    # of widget. Thus, it is guaranteed that self.widget is actually a MolecularStructure instance
    # and we may call our respective action handler.

    @Slot()
    def select_all_atoms_handler(self):
        self.widget.scene.select_all_atoms()

    @Slot()
    def unselect_all_atoms_handler(self):
        self.widget.scene.unselect_all_atoms()

    @Slot()
    def select_toggle_all_atoms_handler(self):
        self.widget.scene.select_toggle_all_atoms()

    @Slot()
    def calc_interat_distance_handler(self):
        self.widget.calc_distance_last2sel_atoms()

    @Slot()
    def calc_interat_angle_handler(self):
        self.widget.calc_angle_last3sel_atoms()

    @Slot()
    def calc_torsion_angle_handler(self):
        self.widget.calc_torsion_last4sel_atoms()

    @Slot()
    def calc_oop_angle_handler(self):
        self.widget.calc_oop_last4sel_atoms()

    @Slot()
    def calc_auto_parameter_handler(self):
        self.widget.calc_auto_lastsel_atoms()

    @Slot()
    def calc_sel_fragments_handler(self):
        self.widget.calc_all_parameters_selected_atoms()

    @Slot()
    def save_img_action_handler(self):
        self.widget.save_img_action_handler()

    @Slot()
    def cloak_selected_handler(self):
        self.widget.scene.cloak_selected_atoms()

    @Slot()
    def cloak_not_selected_handler(self):
        self.widget.scene.cloak_not_selected_atoms()

    @Slot()
    def cloak_h_atoms_handler(self):
        self.widget.scene.cloak_h_atoms()

    @Slot()
    def cloak_toggle_h_atoms_handler(self):
        self.widget.scene.cloak_toggle_h_atoms()

    @Slot()
    def cloak_atoms_by_type_handler(self):
        self.widget.cloak_atoms_by_atnum()

    @Slot()
    def uncloak_all_handler(self):
        self.widget.scene.uncloak_all_atoms()
