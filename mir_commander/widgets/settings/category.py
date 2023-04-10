from PySide6.QtWidgets import QWidget

from mir_commander.settings import Settings
from mir_commander.utils.widget import Translator


class Category(Translator, QWidget):
    """Basic class for each page in the settings dialog.

    The main purpose of this class is to implement the common
    initialization method, see the code below.
    """

    def __init__(self, parent, settings: Settings):
        super().__init__(parent)
        self.settings = settings
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
