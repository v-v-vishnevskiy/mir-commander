from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from mir_commander.utils.widget import Translator

if TYPE_CHECKING:
    from mir_commander.widgets.settings import Settings


class Category(Translator, QWidget):
    """Basic class for each page in the settings dialog.

    The main purpose of this class is to implement the common
    initialization method, see the code below.
    """

    def __init__(self, parent: "Settings"):
        super().__init__(parent)
        self.global_settings = parent.global_settings  # type: ignore
        self.project_settings = parent.project_settings  # type: ignore

        layout = self.setup_ui()
        self.setup_data()
        self.retranslate_ui()
        self.post_init()
        self.setLayout(layout)

    def post_init(self):
        pass

    def setup_ui(self):
        raise NotImplementedError()

    def setup_data(self):
        pass
