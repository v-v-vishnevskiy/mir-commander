from typing import TYPE_CHECKING

from PySide6.QtGui import QKeySequence

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.widget import Action, Menu

if TYPE_CHECKING:
    from .program import MolecularVisualizer


class ContextMenu(Menu):
    def __init__(self, parent: "MolecularVisualizer", app_config: AppConfig):
        super().__init__(parent=parent)

        self._program = parent
        self._visualizer = parent.visualizer
        self._app_config = app_config
        self._config = app_config.project_window.widgets.programs.molecular_visualizer
        self._keymap = self._config.keymap

        self._init_atom_labels_menu()
        self._init_bonds_menu()
        self._init_selection_menu()
        self._init_calculate_menu()
        self._init_cloaking_menu()
        self._switch_atomic_coordinates_menu()
        self.addSeparator()
        self._init_actions()

    def _init_actions(self):
        save_img_act = Action(Action.tr("Save image..."), self.parent())
        save_img_act.setShortcut(QKeySequence(self._keymap.save_image))
        save_img_act.triggered.connect(self._visualizer.save_img_action_handler)
        self.addAction(save_img_act)
        self._visualizer.addAction(save_img_act)

        self.addSeparator()

        next_style_act = Action(Action.tr("Next style"), self.parent())
        next_style_act.setShortcut(QKeySequence(self._keymap.next_style))
        next_style_act.triggered.connect(self._visualizer.set_next_style)
        self.addAction(next_style_act)
        self._visualizer.addAction(next_style_act)

        prev_style_act = Action(Action.tr("Previous style"), self.parent())
        prev_style_act.setShortcut(QKeySequence(self._keymap.prev_style))
        prev_style_act.triggered.connect(self._visualizer.set_prev_style)
        self.addAction(prev_style_act)
        self._visualizer.addAction(prev_style_act)

        self.addSeparator()

        projection_act = Action(Action.tr("Toggle projection"), self.parent())
        projection_act.setShortcut(QKeySequence(self._keymap.toggle_projection))
        projection_act.triggered.connect(self._visualizer.toggle_projection_mode)
        self.addAction(projection_act)
        self._visualizer.addAction(projection_act)

    def _init_atom_labels_menu(self):
        menu = Menu(Menu.tr("Atom labels"))
        self.addMenu(menu)

        show_all_act = Action(Action.tr("Show all"), self.parent())
        show_all_act.setStatusTip(Action.tr("Show labels for all atoms"))
        show_all_act.triggered.connect(self._visualizer.atom_labels_show_for_all_atoms)
        menu.addAction(show_all_act)

        hide_all_act = Action(Action.tr("Hide all"), self.parent())
        hide_all_act.setStatusTip(Action.tr("Hide labels for all atoms"))
        hide_all_act.triggered.connect(self._visualizer.atom_labels_hide_for_all_atoms)
        menu.addAction(hide_all_act)

        menu.addSeparator()

        show_for_selected_atoms_act = Action(Action.tr("Show selected"), self.parent())
        show_for_selected_atoms_act.setStatusTip(Action.tr("Show labels for selected atoms"))
        show_for_selected_atoms_act.triggered.connect(self._visualizer.atom_labels_show_for_selected_atoms)
        menu.addAction(show_for_selected_atoms_act)

        hide_for_selected_atoms_act = Action(Action.tr("Hide selected"), self.parent())
        hide_for_selected_atoms_act.setStatusTip(Action.tr("Hide labels for selected atoms"))
        hide_for_selected_atoms_act.triggered.connect(self._visualizer.atom_labels_hide_for_selected_atoms)
        menu.addAction(hide_for_selected_atoms_act)

        menu.addSeparator()

        toggle_all_act = Action(Action.tr("Toggle all"), self.parent())
        toggle_all_act.setShortcut(QKeySequence(self._keymap.toggle_labels_visibility_for_all_atoms))
        toggle_all_act.setStatusTip(Action.tr("Toggle labels for all atoms"))
        toggle_all_act.triggered.connect(self._visualizer.toggle_labels_visibility_for_all_atoms)
        self._visualizer.addAction(toggle_all_act)
        menu.addAction(toggle_all_act)

        toggle_selected_act = Action(Action.tr("Toggle selected"), self.parent())
        toggle_selected_act.setShortcut(QKeySequence(self._keymap.toggle_labels_visibility_for_selected_atoms))
        toggle_selected_act.setStatusTip(Action.tr("Toggle labels for selected atoms"))
        toggle_selected_act.triggered.connect(self._visualizer.toggle_labels_visibility_for_selected_atoms)
        self._visualizer.addAction(toggle_selected_act)
        menu.addAction(toggle_selected_act)

    def _init_bonds_menu(self):
        bonds_menu = Menu(Menu.tr("Bonds"))
        self.addMenu(bonds_menu)

        add_selected_act = Action(Action.tr("Add selected"), self.parent())
        add_selected_act.setStatusTip(Action.tr("Add new bonds between selected atoms"))
        add_selected_act.triggered.connect(self._visualizer.add_bonds_for_selected_atoms)
        bonds_menu.addAction(add_selected_act)

        remove_selected_act = Action(Action.tr("Remove selected"), self.parent())
        remove_selected_act.setStatusTip(Action.tr("Remove existing bonds between selected atoms"))
        remove_selected_act.triggered.connect(self._visualizer.remove_bonds_for_selected_atoms)
        bonds_menu.addAction(remove_selected_act)

        toggle_selected_act = Action(Action.tr("Toggle selected"), self.parent())
        toggle_selected_act.setShortcut(QKeySequence(self._keymap.toggle_selected))
        toggle_selected_act.setStatusTip(Action.tr("Add new or remove existing bonds between selected atoms"))
        toggle_selected_act.triggered.connect(self._visualizer.toggle_bonds_for_selected_atoms)
        bonds_menu.addAction(toggle_selected_act)
        self._visualizer.addAction(toggle_selected_act)

        build_dynamically_act = Action(Action.tr("Build dynamically..."), self.parent())
        build_dynamically_act.setStatusTip(Action.tr("Build bonds in dynamic mode by adjusting settings"))
        build_dynamically_act.triggered.connect(self._visualizer.rebuild_bonds_dynamic)
        bonds_menu.addAction(build_dynamically_act)

        rebuild_all_act = Action(Action.tr("Rebuild all"), self.parent())
        rebuild_all_act.setStatusTip(Action.tr("Remove all current bonds and automatically create a new set of bonds"))
        rebuild_all_act.triggered.connect(self._visualizer.rebuild_bonds)
        bonds_menu.addAction(rebuild_all_act)

        rebuild_default_act = Action(Action.tr("Rebuild default"), self.parent())
        rebuild_default_act.setStatusTip(Action.tr("Rebuild bonds automatically using default settings"))
        rebuild_default_act.triggered.connect(self._visualizer.rebuild_bonds_default)
        bonds_menu.addAction(rebuild_default_act)

    def _init_selection_menu(self):
        selection_menu = Menu(Menu.tr("Selection"))
        self.addMenu(selection_menu)

        select_all_atoms_act = Action(Action.tr("Select all atoms"), self.parent())
        select_all_atoms_act.triggered.connect(self._visualizer.select_all_atoms)
        selection_menu.addAction(select_all_atoms_act)

        unselect_all_atoms_act = Action(Action.tr("Unselect all atoms"), self.parent())
        unselect_all_atoms_act.triggered.connect(self._visualizer.unselect_all_atoms)
        selection_menu.addAction(unselect_all_atoms_act)

        select_toggle_all_atoms_act = Action(Action.tr("Toggle all atoms"), self.parent())
        select_toggle_all_atoms_act.setShortcut(QKeySequence(self._keymap.select_toggle_all))
        select_toggle_all_atoms_act.triggered.connect(self._visualizer.select_toggle_all_atoms)
        selection_menu.addAction(select_toggle_all_atoms_act)
        self._visualizer.addAction(select_toggle_all_atoms_act)

    def _init_calculate_menu(self):
        calc_menu = Menu(Menu.tr("Calculate"))
        self.addMenu(calc_menu)

        calc_interat_distance_act = Action(Action.tr("Interatomic distance"), self.parent())
        calc_interat_distance_act.setStatusTip(Action.tr("Distance between last two selected atoms a1-a2"))
        calc_interat_distance_act.triggered.connect(self._visualizer.calc_distance_last2sel_atoms)
        calc_menu.addAction(calc_interat_distance_act)

        calc_interat_angle_act = Action(Action.tr("Interatomic angle"), self.parent())
        calc_interat_angle_act.setStatusTip(
            Action.tr("Angle between two lines formed by last three selected atoms a1-a2-a3")
        )
        calc_interat_angle_act.triggered.connect(self._visualizer.calc_angle_last3sel_atoms)
        calc_menu.addAction(calc_interat_angle_act)

        calc_torsion_angle_act = Action(Action.tr("Torsion angle"), self.parent())
        calc_torsion_angle_act.setStatusTip(
            Action.tr(
                "Dihedral angle between two planes (a1-a2-a3) and (a2-a3-a4) "
                "defined on the basis of last four selected atoms"
            )
        )
        calc_torsion_angle_act.triggered.connect(self._visualizer.calc_torsion_last4sel_atoms)
        calc_menu.addAction(calc_torsion_angle_act)

        calc_oop_angle_act = Action(Action.tr("Out-of-plane angle"), self.parent())
        calc_oop_angle_act.setStatusTip(
            Action.tr(
                "Angle between the vector (a1-a2) and plane (a3-a2-a4) defined on the basis of last four selected atoms"
            )
        )
        calc_oop_angle_act.triggered.connect(self._visualizer.calc_oop_last4sel_atoms)
        calc_menu.addAction(calc_oop_angle_act)

        calc_auto_parameter_act = Action(Action.tr("Auto parameter"), self.parent())
        calc_auto_parameter_act.setShortcut(QKeySequence(self._keymap.calc_auto_parameter))
        calc_auto_parameter_act.setStatusTip(
            Action.tr("Interatomic distance, angle or torsion angle if two, three or four atoms are selected")
        )
        calc_auto_parameter_act.triggered.connect(self._visualizer.calc_auto_lastsel_atoms)
        calc_menu.addAction(calc_auto_parameter_act)
        self._visualizer.addAction(calc_auto_parameter_act)

        calc_sel_fragments_act = Action(Action.tr("Selected fragments"), self.parent())
        calc_sel_fragments_act.setStatusTip(
            Action.tr("Calculate all geometric parameters for fragments with selected atoms")
        )
        calc_sel_fragments_act.triggered.connect(self._visualizer.calc_all_parameters_selected_atoms)
        calc_menu.addAction(calc_sel_fragments_act)

    def _init_cloaking_menu(self):
        cloaking_menu = Menu(Menu.tr("Cloaking"))
        self.addMenu(cloaking_menu)

        cloak_selected_act = Action(Action.tr("Cloak all selected"), self.parent())
        cloak_selected_act.triggered.connect(self._visualizer.cloak_selected_atoms)
        cloaking_menu.addAction(cloak_selected_act)

        cloak_not_selected_act = Action(Action.tr("Cloak all not selected"), self.parent())
        cloak_not_selected_act.triggered.connect(self._visualizer.cloak_not_selected_atoms)
        cloaking_menu.addAction(cloak_not_selected_act)

        cloak_h_atoms_act = Action(Action.tr("Cloak all H atoms"), self.parent())
        cloak_h_atoms_act.triggered.connect(self._visualizer.cloak_h_atoms)
        cloaking_menu.addAction(cloak_h_atoms_act)

        cloak_notsel_h_atoms_act = Action(Action.tr("Cloak not selected H atoms"), self.parent())
        cloak_notsel_h_atoms_act.triggered.connect(self._visualizer.cloak_not_selected_h_atoms)
        cloaking_menu.addAction(cloak_notsel_h_atoms_act)

        cloak_toggle_h_atoms_act = Action(Action.tr("Toggle all H atoms"), self.parent())
        cloak_toggle_h_atoms_act.setShortcut(QKeySequence(self._keymap.cloak_toggle_h_atoms))
        cloak_toggle_h_atoms_act.triggered.connect(self._visualizer.cloak_toggle_h_atoms)
        cloaking_menu.addAction(cloak_toggle_h_atoms_act)
        self._visualizer.addAction(cloak_toggle_h_atoms_act)

        cloak_at_by_type_act = Action(Action.tr("Cloak atoms by type..."), self.parent())
        cloak_at_by_type_act.triggered.connect(self._visualizer.cloak_atoms_by_atnum)
        cloaking_menu.addAction(cloak_at_by_type_act)

        cloaking_menu.addSeparator()

        uncloak_all_act = Action(Action.tr("Uncloak all"), self.parent())
        uncloak_all_act.triggered.connect(self._visualizer.uncloak_all_atoms)
        cloaking_menu.addAction(uncloak_all_act)

    def _switch_atomic_coordinates_menu(self):
        menu = Menu(Menu.tr("Coordinates set"))
        self.addMenu(menu)

        next_atomic_coordinates_act = Action(Action.tr("Next"), self.parent())
        next_atomic_coordinates_act.setShortcut(QKeySequence(self._keymap.next_atomic_coordinates))
        next_atomic_coordinates_act.triggered.connect(self._program.set_next_atomic_coordinates)
        menu.addAction(next_atomic_coordinates_act)
        self._program.addAction(next_atomic_coordinates_act)

        prev_atomic_coordinates_act = Action(Action.tr("Previous"), self.parent())
        prev_atomic_coordinates_act.setShortcut(QKeySequence(self._keymap.prev_atomic_coordinates))
        prev_atomic_coordinates_act.triggered.connect(self._program.set_prev_atomic_coordinates)
        menu.addAction(prev_atomic_coordinates_act)
        self._program.addAction(prev_atomic_coordinates_act)
