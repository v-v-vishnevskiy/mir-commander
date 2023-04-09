from PySide6.QtWidgets import QPlainTextEdit


class Console(QPlainTextEdit):
    """The class of widgets for showing multi-line text information.

    For example, such widgets may be used for showing rerults of calculations.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
