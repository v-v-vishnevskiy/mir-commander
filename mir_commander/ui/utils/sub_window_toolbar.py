from typing import TYPE_CHECKING, Union

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMdiSubWindow, QWidget

from mir_commander.ui.utils.widget import ToolBar as ToolBarWidget

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class SubWindowToolBar(ToolBarWidget):
    widget: QWidget = None

    def __init__(self, title: str, parent: "MainWindow"):
        super().__init__(title, parent)
        self.mdi_area = parent.mdi_area

        icon_size = parent.app.config["widgets.toolbars.icon_size"]
        self.setIconSize(QSize(icon_size, icon_size))

        self.setup_actions()
        self.set_enabled(False)

    def setup_actions(self):
        raise NotImplementedError()

    def set_enabled(self, flag: bool):
        for action in self.actions():
            action.setEnabled(flag)

    def update_state(self, window: Union[None, QMdiSubWindow]):
        if window and type(window.widget()) == self.widget:
            self.set_enabled(True)
        else:
            self.set_enabled(False)
