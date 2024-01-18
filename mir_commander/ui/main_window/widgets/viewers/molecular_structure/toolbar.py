from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

from mir_commander.ui.main_window.widgets.viewers.molecular_structure.viewer import MolecularStructure
from mir_commander.ui.utils.sub_window_toolbar import SubWindowToolBar
from mir_commander.ui.utils.widget import Action

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class ToolBar(SubWindowToolBar):
    widget: QWidget = MolecularStructure

    def __init__(self, parent: "MainWindow"):
        super().__init__(ToolBar.tr("Molecular viewer"), parent)
        self.setObjectName("Molecular viewer")

    def setup_actions(self):
        cloak_toggle_h_atoms_act = Action(Action.tr("Toggle visibility of H atoms"), self.parent())
        cloak_toggle_h_atoms_act.setIcon(QIcon(":/icons/actions/hydrogen_symbol.png"))
        cloak_toggle_h_atoms_act.triggered.connect(self.cloak_toggle_h_atoms_handler)
        self.addAction(cloak_toggle_h_atoms_act)

        select_toggle_all_atoms_act = Action(Action.tr("Toggle selection of all atoms"), self.parent())
        select_toggle_all_atoms_act.setIcon(QIcon(":/icons/actions/toggle_all_selection.png"))
        select_toggle_all_atoms_act.triggered.connect(self.select_toggle_all_atoms_handler)
        self.addAction(select_toggle_all_atoms_act)

        calc_auto_parameter_act = Action(Action.tr("Auto calculate parameter"), self.parent())
        calc_auto_parameter_act.setIcon(QIcon(":/icons/actions/triangular_ruler.png"))
        calc_auto_parameter_act.triggered.connect(self.calc_auto_parameter_handler)
        self.addAction(calc_auto_parameter_act)

        save_img_act = Action(Action.tr("Save image..."), self.parent())
        save_img_act.setIcon(QIcon(":/icons/actions/saveimage.png"))
        save_img_act.triggered.connect(self.save_img_action_handler)
        self.addAction(save_img_act)

    @Slot()
    def cloak_toggle_h_atoms_handler(self):
        self.mdi_area.activeSubWindow().widget().scene.cloak_toggle_h_atoms()

    @Slot()
    def select_toggle_all_atoms_handler(self):
        self.mdi_area.activeSubWindow().widget().scene.select_toggle_all_atoms()

    @Slot()
    def calc_auto_parameter_handler(self):
        self.mdi_area.activeSubWindow().widget().calc_auto_lastsel_atoms()

    @Slot()
    def save_img_action_handler(self):
        # Note, this callback is only triggered, when the respective action is enabled.
        # Whether this is the case, is determined by the update_state method of the SubWindowToolBar class.
        # This method receives the window parameter, so it is possible to determine the currently active type
        # of widget. Thus, it is guaranteed that mdi_area.activeSubWindow() is actually a MolViewer instance
        # and we may call save_img_action_handler().
        self.mdi_area.activeSubWindow().widget().save_img_action_handler()
