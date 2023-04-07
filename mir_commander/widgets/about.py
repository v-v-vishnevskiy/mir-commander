from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from mir_commander import __version__
from mir_commander.utils.widget import Translator


class About(Translator, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        label = QLabel(self)
        pixmap = QPixmap(":/icons/general/app.svg")
        label.setPixmap(pixmap.scaledToWidth(150, mode=Qt.SmoothTransformation))
        layout.addWidget(label, 100, Qt.AlignCenter)
        layout.addWidget(QLabel(f"Mir Commander {__version__}"), 100, Qt.AlignCenter)
        self.authorlabel1 = QLabel(self)
        self.authorlabel2 = QLabel(self)
        layout.addWidget(self.authorlabel1, 0, Qt.AlignCenter)
        layout.addWidget(self.authorlabel2, 0, Qt.AlignCenter)

        self.setLayout(layout)
        self.setFixedSize(400, 300)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("About Mir Commander"))
        self.authorlabel1.setText(self.tr("Yury V. Vishnevskiy"))
        self.authorlabel2.setText(self.tr("Valery V. Vishnevskiy"))
