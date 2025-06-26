from typing import Any, TYPE_CHECKING

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from mir_commander.ui.widgets.settings.settings_dialog import SettingsDialog


class BasePage(QWidget):
    """Basic class for each page in the settings dialog.

    The main purpose of this class is to implement the common
    initialization method, see the code below.
    """

    def __init__(self, parent: "SettingsDialog"):
        super().__init__(parent)
        self.app_config = parent.app_config
        self.project_config = parent.project_config
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
