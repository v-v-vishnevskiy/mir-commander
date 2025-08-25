from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMdiArea, QWidget

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.viewer import ViewerToolBar
from mir_commander.ui.utils.widget import Action

from .atomic_coordinates_viewer import AtomicCoordinatesViewer
from .viewer import MolecularStructureViewer


class ToolBar(ViewerToolBar[MolecularStructureViewer]):
    def __init__(self, parent: QWidget, mdi_area: QMdiArea, app_config: AppConfig):
        super().__init__(ToolBar.tr("Molecular viewer"), parent, mdi_area, app_config)
        self.setObjectName("Molecular Structure Toolbar")

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

        next_atomic_coordinates_act = Action(Action.tr("Next coordinates set"), self.parent())
        next_atomic_coordinates_act.setIcon(QIcon(":/icons/actions/next-coordinates-set.png"))
        next_atomic_coordinates_act.triggered.connect(self.next_atomic_coordinates_action_handler)
        self.addAction(next_atomic_coordinates_act)

        prev_atomic_coordinates_act = Action(Action.tr("Previous coordinates set"), self.parent())
        prev_atomic_coordinates_act.setIcon(QIcon(":/icons/actions/prev-coordinates-set.png"))
        prev_atomic_coordinates_act.triggered.connect(self.prev_atomic_coordinates_action_handler)
        self.addAction(prev_atomic_coordinates_act)

        next_style_act = Action(Action.tr("Next style"), self.parent())
        next_style_act.setIcon(QIcon(":/icons/actions/next-style.png"))
        next_style_act.triggered.connect(self.next_style_action_handler)
        self.addAction(next_style_act)

        prev_style_act = Action(Action.tr("Previous style"), self.parent())
        prev_style_act.setIcon(QIcon(":/icons/actions/prev-style.png"))
        prev_style_act.triggered.connect(self.prev_style_action_handler)
        self.addAction(prev_style_act)

    @property
    def active_ac_viewer(self) -> AtomicCoordinatesViewer:
        return super().active_viewer.ac_viewer

    @Slot()
    def cloak_toggle_h_atoms_handler(self):
        self.active_ac_viewer.cloak_toggle_h_atoms()

    @Slot()
    def select_toggle_all_atoms_handler(self):
        self.active_ac_viewer.select_toggle_all_atoms()

    @Slot()
    def calc_auto_parameter_handler(self):
        self.active_ac_viewer.calc_auto_lastsel_atoms()

    @Slot()
    def save_img_action_handler(self):
        # Note, this callback is only triggered, when the respective action is enabled.
        # Whether this is the case, is determined by the update_state method of the SubWindowToolBar class.
        # This method receives the window parameter, so it is possible to determine the currently active type
        # of widget. Thus, it is guaranteed that self.widget is actually a MolecularStructure instance
        # and we may call save_img_action_handler().
        filename = self.active_viewer._draw_item.text()
        self.active_ac_viewer.save_img_action_handler(filename)

    @Slot()
    def next_atomic_coordinates_action_handler(self):
        self.active_viewer.set_next_atomic_coordinates()

    @Slot()
    def prev_atomic_coordinates_action_handler(self):
        self.active_viewer.set_prev_atomic_coordinates()

    @Slot()
    def next_style_action_handler(self):
        self.active_ac_viewer.set_next_style()

    @Slot()
    def prev_style_action_handler(self):
        self.active_ac_viewer.set_prev_style()
