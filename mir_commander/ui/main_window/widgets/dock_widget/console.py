from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QPlainTextEdit, QWidget

from mir_commander.ui.main_window.widgets.dock_widget.base import DockWidget
from mir_commander.utils.config import Config


class Text(QPlainTextEdit):
    """The class of widgets for showing multi-line text information.

    For example, such widgets may be used for showing results of calculations.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setReadOnly(True)


class Console(DockWidget):
    """The console dockable widget.

    Contains an instance of the Text widget for showing text information.
    """

    default_area = Qt.BottomDockWidgetArea

    def __init__(self, parent: QMainWindow, config: Config):
        super().__init__(self.tr("Console output"), config, parent)
        self.text = Text(self)
        self.setWidget(self.text)

    def append(self, text: str):
        self.text.appendPlainText(text)
