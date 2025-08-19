from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QVBoxLayout

from mir_commander.ui.utils.widget import Label

from .base import BasePage


class Project(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addLayout(self._project_name_ui)
        layout.addStretch(1)

        return layout

    def backup_data(self):
        self._backup["project_name"] = self.project_config.name

    def restore_backup_data(self):
        self.project_config.name = self._backup["project_name"]

    def setup_data(self):
        self._setup_project_name_data()

    def post_init(self):
        self.le_project_name.textChanged.connect(self._project_name_changed)

    @property
    def _project_name_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self.l_project_name = Label(Label.tr("Project name:"))
        self.le_project_name = QLineEdit()

        layout.addWidget(self.l_project_name, 0, Qt.AlignLeft)
        layout.addWidget(self.le_project_name, 1, Qt.AlignLeft)

        return layout

    def _setup_project_name_data(self):
        self.le_project_name.setText(self.project_config.name)

    @Slot()
    def _project_name_changed(self, text: str):
        self.project_config.name = text
