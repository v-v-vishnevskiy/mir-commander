from typing import TYPE_CHECKING

from PySide6.QtWidgets import QMdiSubWindow, QWidget

from mir_commander.ui.utils.widget import Menu

if TYPE_CHECKING:
    from mir_commander.ui.main_window import MainWindow


class SubWindowMenu(Menu):
    widget: QWidget = None

    def __init__(self, title: str, parent: "MainWindow"):
        super().__init__(title, parent)
        self.mdi_area = parent.mdi_area

    def update_state(self, window: None | QMdiSubWindow):
        if window and type(window.widget()) == self.widget:
            self.set_enabled(True)
        else:
            self.set_enabled(False)
