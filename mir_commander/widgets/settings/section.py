from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QWidget


class Section(QWidget):
    def __init__(self, parent, settings: QSettings):
        super().__init__(parent)
        self.settings = settings
        layout = self.setup_ui()
        self.setup_data()
        self.setLayout(layout)

    def setup_ui(self):
        raise NotImplementedError()

    def setup_data(self):
        pass
