from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon, QKeySequence
from PySide6.QtWidgets import QMdiArea, QWidget

from mir_commander.ui.utils.sub_window_menu import SubWindowMenu
from mir_commander.ui.utils.widget import Action
from mir_commander.ui.utils.widget import Menu as BaseMenu

from .config import AtomLabelType, MolecularStructureViewerConfig
from .label_settings_dialog import LabelSettingsDialog
from .viewer import MolecularStructureViewer


class Menu(SubWindowMenu[MolecularStructureViewer]):
    def __init__(self, parent: QWidget, mdi_area: QMdiArea, config: MolecularStructureViewerConfig):
        super().__init__(Menu.tr("&Molecule"), parent, mdi_area)
        self.setObjectName("Molecular Structure Menu")

        self._config = config
        self._keymap = config.keymap.menu
        self._style = config.get_current_style()

        self._init_atom_labels_menu()
        self._init_bonds_menu()
        self._init_selection_menu()
        self._init_calculate_menu()
        self._init_cloaking_menu()
        self._switch_atomic_coordinates_menu()
        self._style_menu()

        projection_act = Action(Action.tr("Toggle projection"), self.parent())
        projection_act.setShortcut(QKeySequence(self._keymap.toggle_projection))
        projection_act.triggered.connect(self.toggle_projection_action_handler)
        self.addAction(projection_act)

        save_img_act = Action(Action.tr("Save image..."), self.parent())
        save_img_act.setShortcut(QKeySequence(self._keymap.save_image))
        save_img_act.setIcon(QIcon(":/icons/actions/saveimage.png"))
        save_img_act.triggered.connect(self.save_img_action_handler)
        self.addAction(save_img_act)

        self.set_enabled_actions(False)

    def _init_atom_labels_menu(self):
        menu = BaseMenu(Menu.tr("Atom labels"))
        self.addMenu(menu)

        show_for_selected_atoms_act = Action(Action.tr("Show for selected atoms"), self.parent())
        show_for_selected_atoms_act.setStatusTip(Action.tr("Show labels for selected atoms"))
        show_for_selected_atoms_act.triggered.connect(self.labels_show_for_selected_atoms_handler)
        menu.addAction(show_for_selected_atoms_act)

        hide_for_selected_atoms_act = Action(Action.tr("Hide for selected atoms"), self.parent())
        hide_for_selected_atoms_act.setStatusTip(Action.tr("Hide labels for selected atoms"))
        hide_for_selected_atoms_act.triggered.connect(self.labels_hide_for_selected_atoms_handler)
        menu.addAction(hide_for_selected_atoms_act)

        menu.addSeparator()

        self.set_element_symbol_and_index_number_act = Action(
            Action.tr("Set element symbol and index number"),
            self.parent(),
            checkable=True,
            checked=self._config.atom_label.type == AtomLabelType.ELEMENT_SYMBOL_AND_INDEX_NUMBER,
        )
        self.set_element_symbol_and_index_number_act.setStatusTip(
            Action.tr("Show element symbol and index number as label")
        )
        self.set_element_symbol_and_index_number_act.triggered.connect(
            self.labels_set_element_symbol_and_index_number_handler
        )
        menu.addAction(self.set_element_symbol_and_index_number_act)

        self.set_element_symbol_act = Action(
            Action.tr("Set element symbol"),
            self.parent(),
            checkable=True,
            checked=self._config.atom_label.type == AtomLabelType.ELEMENT_SYMBOL,
        )
        self.set_element_symbol_act.setStatusTip(Action.tr("Show element symbol as label"))
        self.set_element_symbol_act.triggered.connect(self.labels_set_element_symbol_handler)
        menu.addAction(self.set_element_symbol_act)

        self.set_index_number_act = Action(
            Action.tr("Set index number"),
            self.parent(),
            checkable=True,
            checked=self._config.atom_label.type == AtomLabelType.INDEX_NUMBER,
        )
        self.set_index_number_act.setStatusTip(Action.tr("Show index number as label"))
        self.set_index_number_act.triggered.connect(self.labels_set_index_number_handler)
        menu.addAction(self.set_index_number_act)

        menu.addSeparator()

        show_all_act = Action(Action.tr("Show all"), self.parent())
        show_all_act.setStatusTip(Action.tr("Show labels for all atoms"))
        show_all_act.triggered.connect(self.labels_show_for_all_atoms_handler)
        menu.addAction(show_all_act)

        hide_all_act = Action(Action.tr("Hide all"), self.parent())
        hide_all_act.setStatusTip(Action.tr("Hide labels for all atoms"))
        hide_all_act.triggered.connect(self.labels_hide_for_all_atoms_handler)
        menu.addAction(hide_all_act)

        menu.addSeparator()

        label_size_act = Action(Action.tr("Label size settings..."), self.parent())
        label_size_act.setStatusTip(Action.tr("Adjust label size for all atoms"))
        label_size_act.triggered.connect(self.labels_size_settings_handler)
        menu.addAction(label_size_act)

    def _init_bonds_menu(self):
        bonds_menu = BaseMenu(Menu.tr("Bonds"))
        self.addMenu(bonds_menu)

        add_selected_act = Action(Action.tr("Add selected"), self.parent())
        add_selected_act.setStatusTip(Action.tr("Add new bonds between selected atoms"))
        add_selected_act.triggered.connect(self.bonds_add_selected_handler)
        bonds_menu.addAction(add_selected_act)

        remove_selected_act = Action(Action.tr("Remove selected"), self.parent())
        remove_selected_act.setStatusTip(Action.tr("Remove existing bonds between selected atoms"))
        remove_selected_act.triggered.connect(self.bonds_remove_selected_handler)
        bonds_menu.addAction(remove_selected_act)

        toggle_selected_act = Action(Action.tr("Toggle selected"), self.parent())
        toggle_selected_act.setShortcut(QKeySequence(self._keymap.toggle_selected))
        toggle_selected_act.setStatusTip(Action.tr("Add new or remove existing bonds between selected atoms"))
        toggle_selected_act.triggered.connect(self.bonds_toggle_selected_handler)
        bonds_menu.addAction(toggle_selected_act)

        build_dynamically_act = Action(Action.tr("Build dynamically..."), self.parent())
        build_dynamically_act.setStatusTip(Action.tr("Build bonds in dynamic mode by adjusting settings"))
        build_dynamically_act.triggered.connect(self.bonds_build_dynamically_handler)
        bonds_menu.addAction(build_dynamically_act)

        rebuild_all_act = Action(Action.tr("Rebuild all"), self.parent())
        rebuild_all_act.setStatusTip(Action.tr("Remove all current bonds and automatically create a new set of bonds"))
        rebuild_all_act.triggered.connect(self.bonds_rebuild_all_handler)
        bonds_menu.addAction(rebuild_all_act)

        rebuild_default_act = Action(Action.tr("Rebuild default"), self.parent())
        rebuild_default_act.setStatusTip(Action.tr("Rebuild bonds automatically using default settings"))
        rebuild_default_act.triggered.connect(self.bonds_rebuild_default_handler)
        bonds_menu.addAction(rebuild_default_act)

    def _init_selection_menu(self):
        selection_menu = BaseMenu(Menu.tr("Selection"))
        self.addMenu(selection_menu)

        select_all_atoms_act = Action(Action.tr("Select all atoms"), self.parent())
        select_all_atoms_act.triggered.connect(self.select_all_atoms_handler)
        selection_menu.addAction(select_all_atoms_act)

        unselect_all_atoms_act = Action(Action.tr("Unselect all atoms"), self.parent())
        unselect_all_atoms_act.triggered.connect(self.unselect_all_atoms_handler)
        selection_menu.addAction(unselect_all_atoms_act)

        select_toggle_all_atoms_act = Action(Action.tr("Toggle all atoms"), self.parent())
        select_toggle_all_atoms_act.setShortcut(QKeySequence(self._keymap.select_toggle_all))
        select_toggle_all_atoms_act.triggered.connect(self.select_toggle_all_atoms_handler)
        selection_menu.addAction(select_toggle_all_atoms_act)

    def _init_calculate_menu(self):
        calc_menu = BaseMenu(Menu.tr("Calculate"))
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
        calc_auto_parameter_act.setShortcut(QKeySequence(self._keymap.calc_auto_parameter))
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
        cloaking_menu = BaseMenu(Menu.tr("Cloaking"))
        self.addMenu(cloaking_menu)

        cloak_selected_act = Action(Action.tr("Cloak all selected"), self.parent())
        cloak_selected_act.triggered.connect(self.cloak_selected_handler)
        cloaking_menu.addAction(cloak_selected_act)

        cloak_not_selected_act = Action(Action.tr("Cloak all not selected"), self.parent())
        cloak_not_selected_act.triggered.connect(self.cloak_not_selected_handler)
        cloaking_menu.addAction(cloak_not_selected_act)

        cloak_h_atoms_act = Action(Action.tr("Cloak all H atoms"), self.parent())
        cloak_h_atoms_act.triggered.connect(self.cloak_h_atoms_handler)
        cloaking_menu.addAction(cloak_h_atoms_act)

        cloak_notsel_h_atoms_act = Action(Action.tr("Cloak not selected H atoms"), self.parent())
        cloak_notsel_h_atoms_act.triggered.connect(self.cloak_notsel_h_atoms_handler)
        cloaking_menu.addAction(cloak_notsel_h_atoms_act)

        cloak_toggle_h_atoms_act = Action(Action.tr("Toggle all H atoms"), self.parent())
        cloak_toggle_h_atoms_act.setShortcut(QKeySequence(self._keymap.cloak_toggle_h_atoms))
        cloak_toggle_h_atoms_act.triggered.connect(self.cloak_toggle_h_atoms_handler)
        cloaking_menu.addAction(cloak_toggle_h_atoms_act)

        cloak_at_by_type_act = Action(Action.tr("Cloak atoms by type..."), self.parent())
        cloak_at_by_type_act.triggered.connect(self.cloak_atoms_by_type_handler)
        cloaking_menu.addAction(cloak_at_by_type_act)

        cloaking_menu.addSeparator()

        uncloak_all_act = Action(Action.tr("Uncloak all"), self.parent())
        uncloak_all_act.triggered.connect(self.uncloak_all_handler)
        cloaking_menu.addAction(uncloak_all_act)

    def _switch_atomic_coordinates_menu(self):
        menu = BaseMenu(Menu.tr("Coordinates set"))
        self.addMenu(menu)

        next_atomic_coordinates_act = Action(Action.tr("Next"), self.parent())
        next_atomic_coordinates_act.setShortcut(QKeySequence(self._keymap.next_atomic_coordinates))
        next_atomic_coordinates_act.triggered.connect(self.next_atomic_coordinates_handler)
        menu.addAction(next_atomic_coordinates_act)

        prev_atomic_coordinates_act = Action(Action.tr("Previous"), self.parent())
        prev_atomic_coordinates_act.setShortcut(QKeySequence(self._keymap.prev_atomic_coordinates))
        prev_atomic_coordinates_act.triggered.connect(self.prev_atomic_coordinates_handler)
        menu.addAction(prev_atomic_coordinates_act)

    def _style_menu(self):
        menu = BaseMenu(Menu.tr("Style"))
        self.addMenu(menu)

        next_style_act = Action(Action.tr("Next"), self.parent())
        next_style_act.setShortcut(QKeySequence(self._keymap.next_style))
        next_style_act.triggered.connect(self.next_style_handler)
        menu.addAction(next_style_act)

        prev_style_act = Action(Action.tr("Previous"), self.parent())
        prev_style_act.setShortcut(QKeySequence(self._keymap.prev_style))
        prev_style_act.triggered.connect(self.prev_style_handler)
        menu.addAction(prev_style_act)

    # Note, callbacks are only triggered, when the respective action is enabled.
    # Whether this is the case, is determined by the update_state method of the SubWindowMenu class.
    # This method receives the window parameter, so it is possible to determine the currently active type
    # of widget. Thus, it is guaranteed that self.widget is actually a MolecularStructure instance
    # and we may call our respective action handler.

    @Slot()
    def toggle_projection_action_handler(self):
        self.widget.toggle_projection_mode()

    @Slot()
    def save_img_action_handler(self):
        self.widget.save_img_action_handler()

    @Slot()
    def bonds_add_selected_handler(self):
        self.widget.add_bonds_for_selected_atoms()

    @Slot()
    def bonds_remove_selected_handler(self):
        self.widget.remove_bonds_for_selected_atoms()

    @Slot()
    def bonds_toggle_selected_handler(self):
        self.widget.toggle_bonds_for_selected_atoms()

    @Slot()
    def bonds_rebuild_all_handler(self):
        self.widget.rebuild_bonds()

    @Slot()
    def bonds_rebuild_default_handler(self):
        self.widget.rebuild_bonds_default()

    @Slot()
    def bonds_build_dynamically_handler(self):
        self.widget.rebuild_bonds_dynamic()

    @Slot()
    def select_all_atoms_handler(self):
        self.widget.select_all_atoms()

    @Slot()
    def unselect_all_atoms_handler(self):
        self.widget.unselect_all_atoms()

    @Slot()
    def select_toggle_all_atoms_handler(self):
        self.widget.select_toggle_all_atoms()

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
    def cloak_selected_handler(self):
        self.widget.cloak_selected_atoms()

    @Slot()
    def cloak_not_selected_handler(self):
        self.widget.cloak_not_selected_atoms()

    @Slot()
    def cloak_h_atoms_handler(self):
        self.widget.cloak_h_atoms()

    @Slot()
    def cloak_notsel_h_atoms_handler(self):
        self.widget.cloak_not_selected_h_atoms()

    @Slot()
    def cloak_toggle_h_atoms_handler(self):
        self.widget.cloak_toggle_h_atoms()

    @Slot()
    def cloak_atoms_by_type_handler(self):
        self.widget.cloak_atoms_by_atnum()

    @Slot()
    def uncloak_all_handler(self):
        self.widget.uncloak_all_atoms()

    @Slot()
    def next_atomic_coordinates_handler(self):
        self.widget.set_next_atomic_coordinates()

    @Slot()
    def prev_atomic_coordinates_handler(self):
        self.widget.set_prev_atomic_coordinates()

    @Slot()
    def next_style_handler(self):
        self.widget.set_next_style()

    @Slot()
    def prev_style_handler(self):
        self.widget.set_prev_style()

    @Slot()
    def labels_show_for_all_atoms_handler(self):
        self.widget.atom_labels_show_for_all_atoms()

    @Slot()
    def labels_hide_for_all_atoms_handler(self):
        self.widget.atom_labels_hide_for_all_atoms()

    @Slot()
    def labels_show_for_selected_atoms_handler(self):
        self.widget.atom_labels_show_for_selected_atoms()

    @Slot()
    def labels_hide_for_selected_atoms_handler(self):
        self.widget.atom_labels_hide_for_selected_atoms()

    @Slot()
    def labels_set_element_symbol_and_index_number_handler(self):
        self.set_index_number_act.setChecked(False)
        self.set_element_symbol_act.setChecked(False)
        self.widget.atom_labels_set_type(AtomLabelType.ELEMENT_SYMBOL_AND_INDEX_NUMBER)

    @Slot()
    def labels_set_element_symbol_handler(self):
        self.set_element_symbol_and_index_number_act.setChecked(False)
        self.set_index_number_act.setChecked(False)
        self.widget.atom_labels_set_type(AtomLabelType.ELEMENT_SYMBOL)

    @Slot()
    def labels_set_index_number_handler(self):
        self.set_element_symbol_and_index_number_act.setChecked(False)
        self.set_element_symbol_act.setChecked(False)
        self.widget.atom_labels_set_type(AtomLabelType.INDEX_NUMBER)

    @Slot()
    def labels_size_settings_handler(self):
        size = self._config.atom_label.size
        dlg = LabelSettingsDialog(self._config.atom_label.size, self.widget)
        if not dlg.exec():
            self.widget.set_label_size_for_all_atoms(size=size)
