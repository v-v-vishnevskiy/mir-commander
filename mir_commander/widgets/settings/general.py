from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QVBoxLayout

from mir_commander.widgets.settings.category import Category


class General(Category):
    """The page with the general settings.

    At this point only implements choosing language.
    The particular UI elements may migrate to other pages.
    """

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addLayout(self._language_ui)
        layout.addStretch(1)

        return layout

    def setup_data(self):
        self._setup_language_data()

    def post_init(self):
        self.cb_language.currentIndexChanged.connect(self._language_changed)

    def retranslate_ui(self):
        self.l_language.setText(self.tr("Language:"))
        self.cb_language.setItemText(0, self.tr("System"))

    @property
    def _language_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self._languages = [("System", "system"), ("English", "en"), ("Русский", "ru")]
        self.cb_language = QComboBox()
        for item in self._languages:
            self.cb_language.addItem(*item)

        self.l_language = QLabel()

        layout.addWidget(self.l_language, 0, Qt.AlignLeft)
        layout.addWidget(self.cb_language, 1, Qt.AlignLeft)

        return layout

    def _setup_language_data(self):
        index = self.cb_language.findData(self.global_settings["language"])
        self.cb_language.setCurrentIndex(index)

    @Slot()
    def _language_changed(self, index: int):
        self.global_settings["language"] = self._languages[index][1]
