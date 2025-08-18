from PySide6.QtWidgets import QPlainTextEdit, QWidget

from .base import BaseDock


class Text(QPlainTextEdit):
    """The class of widgets for showing multi-line text information.

    For example, such widgets may be used for showing results of calculations.
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setReadOnly(True)


class ConsoleDock(BaseDock):
    """The console dockable widget.

    Contains an instance of the Text widget for showing text information.
    """

    def __init__(self, parent: QWidget):
        super().__init__(self.tr("Console output"), parent)
        self.text = Text(self)
        self.setMinimumHeight(50)
        self.setWidget(self.text)

    def append(self, text: str):
        self.text.appendPlainText(text)
