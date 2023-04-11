from PySide6.QtWidgets import QDockWidget, QWidget

from mir_commander.utils.widget import Translator


class DockWidget(Translator, QDockWidget):
    def __init__(self, title: str, parent: QWidget):
        super().__init__(parent)
        self._title = title
        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.tr(self._title))
