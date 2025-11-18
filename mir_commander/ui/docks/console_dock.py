from PySide6.QtWidgets import QPlainTextEdit, QWidget

from mir_commander.ui.sdk.widget import DockWidget


class Text(QPlainTextEdit):
    """The class of widgets for showing multi-line text information.

    For example, such widgets may be used for showing results of calculations.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent=parent)
        self.setReadOnly(True)


class ConsoleDock(DockWidget):
    """The console dockable widget.

    Contains an instance of the Text widget for showing text information.
    """

    def __init__(self, parent: QWidget):
        super().__init__(self.tr("Console output"), parent)
        self._text = Text(self)
        self.setWidget(self._text)

    def append(self, text: str):
        self._text.appendPlainText(text)
