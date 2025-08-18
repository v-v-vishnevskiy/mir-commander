from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout, QWidget

from .labels import Labels


if TYPE_CHECKING:
    from ..viewer import MolecularStructureViewer


class Settings(QWidget):
    def __init__(self, viewer: "MolecularStructureViewer"):
        super().__init__()

        self.labels = Labels(self, viewer)

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.labels)
        self.main_layout.addStretch()

        self.setLayout(self.main_layout)
