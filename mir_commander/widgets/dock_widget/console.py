from PySide6.QtWidgets import QPlainTextEdit, QWidget

from mir_commander import __version__
from mir_commander.widgets.dock_widget.base import DockWidget


class Text(QPlainTextEdit):
    """The class of widgets for showing multi-line text information.

    For example, such widgets may be used for showing results of calculations.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setReadOnly(True)


class Console(DockWidget):
    def __init__(self, parent: QWidget):
        super().__init__("Console output", parent)
        self.text = Text(self)
        self.text.appendPlainText(f"Started Mir Commander {__version__}")
        self.setWidget(self.text)
