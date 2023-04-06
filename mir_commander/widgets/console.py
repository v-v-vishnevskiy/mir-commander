from PySide6.QtWidgets import QPlainTextEdit


class Console(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
