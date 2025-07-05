from typing import Any

from PySide6.QtWidgets import QWidget

from mir_commander.core.config import ProjectConfig
from mir_commander.ui.config import AppConfig


class BasePage(QWidget):
    """Basic class for each page in the settings dialog.

    The main purpose of this class is to implement the common
    initialization method, see the code below.
    """

    def __init__(self, parent: QWidget, app_config: AppConfig, project_config: ProjectConfig):
        super().__init__(parent)
        self.app_config = app_config
        self.project_config = project_config
        self._backup: dict[str, Any] = {}

        layout = self.setup_ui()
        self.backup_data()
        self.setup_data()
        self.post_init()
        self.setLayout(layout)

    def post_init(self):
        pass

    def setup_ui(self):
        raise NotImplementedError()
    
    def backup_data(self):
        pass

    def restore_backup_data(self):
        pass

    def setup_data(self):
        pass

    def cancel(self):
        self.restore_backup_data()
        self.setup_data()

    def restore_defaults(self):
        pass
