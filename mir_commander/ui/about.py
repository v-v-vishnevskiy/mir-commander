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
        pixmap = QPixmap(":/core/icons/app.png")
        pixmap.setDevicePixelRatio(5.0)
        label.setPixmap(pixmap)
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(5)
        title_label = QLabel("Mir Commander")
        title_label.setObjectName("mircmd-about-title-label")
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel(f"Version {__version__}"), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(QLabel(self.tr("Yury V. Vishnevskiy"), self), alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(QLabel(self.tr("Valery V. Vishnevskiy"), self), alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        self.setWindowTitle(self.tr("About Mir Commander"))
