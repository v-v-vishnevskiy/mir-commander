from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget

from mir_commander.ui.main_window.widgets.viewers.molecular_structure.viewer_new import MolecularStructureNew
from mir_commander.ui.utils.sub_window_toolbar import SubWindowToolBar
from mir_commander.ui.utils.widget import Action

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class ToolBar(SubWindowToolBar):
    widget: QWidget = MolecularStructureNew

    def __init__(self, parent: "MainWindow"):
        super().__init__(ToolBar.tr("Molecular viewer"), parent)
        self.setObjectName("Molecular viewer")

    def setup_actions(self):
        save_img_action = Action(Action.tr("Save image..."), self.parent())
        save_img_action.setIcon(QIcon(":/icons/actions/saveimage.png"))
        save_img_action.triggered.connect(self.save_img_action_handler)
        self.addAction(save_img_action)

    @Slot()
    def save_img_action_handler(self):
        # Note, this callback is only triggered, when the respective action is enabled.
        # Whether this is the case, is determined by the update_state method of the SubWindowToolBar class.
        # This method receives the window parameter, so it is possible to determine the currently active type
        # of widget. Thus, it is guaranteed that mdi_area.activeSubWindow() is actually a MolViewer instance
        # and we may call save_img_action_handler().
        self.mdi_area.activeSubWindow().widget().save_img_action_handler()
