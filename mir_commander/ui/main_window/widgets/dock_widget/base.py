from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QDockWidget, QWidget

from mir_commander.ui.utils.widget import Translator


class DockWidget(Translator, QDockWidget):
    """The basic class for dockable widgets.

    Has been created as a wrapper of QDockWidget
    for simple handling of translation.
    """

    def __init__(self, title: str, parent: QWidget):
        super().__init__(parent)
        self._title = title
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(QCoreApplication.translate("DockNames", self._title))
