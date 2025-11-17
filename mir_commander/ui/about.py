from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from mir_commander import __version__


class About(QDialog):
    """Dialog with information about the program."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        label = QLabel(self)
        pixmap = QPixmap(":/core/icons/app.svg")
        label.setPixmap(pixmap.scaledToWidth(150, mode=Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(label, 100, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel(f"Mir Commander {__version__}"), 100, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel(self.tr("Yury V. Vishnevskiy"), self), 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel(self.tr("Valery V. Vishnevskiy"), self), 0, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.setFixedSize(400, 300)

        self.setWindowTitle(self.tr("About Mir Commander"))
