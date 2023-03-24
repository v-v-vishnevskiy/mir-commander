from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from mir_commander import __version__


class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Mir Commander"), 0, Qt.AlignCenter)
        layout.addWidget(QLabel(f"Version {__version__}"), 0, Qt.AlignCenter)

        self.setLayout(layout)
        self.setFixedSize(400, 300)
