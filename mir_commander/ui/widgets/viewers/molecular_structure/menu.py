from PySide6.QtCore import Slot
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMdiArea, QWidget

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.viewer import ViewerMenu
from mir_commander.ui.utils.widget import Action
from mir_commander.ui.utils.widget import Menu as BaseMenu

from .atomic_coordinates_viewer import AtomicCoordinatesViewer
from .viewer import MolecularStructureViewer


class Menu(ViewerMenu[MolecularStructureViewer]):
    def __init__(self, parent: QWidget, mdi_area: QMdiArea, app_config: AppConfig):
        super().__init__(Menu.tr("&Molecule"), parent, mdi_area)
        self.setObjectName("Molecular Structure Menu")

        self._app_config = app_config

        self._config = app_config.project_window.widgets.viewers.molecular_structure
        self._keymap = self._config.keymap.menu

        self._switch_atomic_coordinates_menu()

        self.set_enabled_actions(False)

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

    @property
    def active_ac_viewer(self) -> AtomicCoordinatesViewer:
        return super().active_viewer.ac_viewer

    @Slot()
    def next_atomic_coordinates_handler(self):
        self.active_viewer.set_next_atomic_coordinates()

    @Slot()
    def prev_atomic_coordinates_handler(self):
        self.active_viewer.set_prev_atomic_coordinates()
