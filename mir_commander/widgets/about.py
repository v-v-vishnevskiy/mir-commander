from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from mir_commander import __version__


class About(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About Mir Commander")

        layout = QVBoxLayout()
        label = QLabel(self)
        pixmap = QPixmap("resources/appicon.svg")
        label.setPixmap(pixmap.scaledToWidth(150, mode=Qt.SmoothTransformation))
        layout.addWidget(label, 100, Qt.AlignCenter)
        layout.addWidget(QLabel(f"Mir Commander {__version__}"), 100, Qt.AlignCenter)
        layout.addWidget(QLabel("Yury V. Vishnevskiy"), 0, Qt.AlignCenter)
        layout.addWidget(QLabel("Valery V. Vishnevskiy"), 0, Qt.AlignCenter)

        self.setLayout(layout)
        self.setFixedSize(400, 300)
