from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from mir_commander.ui.config import AppConfig
from mir_commander.ui.utils.widget import ComboBox, Label

from .base import BasePage


class General(BasePage):
    """The page with the general settings.

    At this point only implements choosing language.
    The particular UI elements may migrate to other pages.
    """

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.addLayout(self._language_ui)
        layout.addStretch(1)

        return layout

    def backup_data(self):
        self._backup["language"] = self.app_config.language

    def restore_backup_data(self):
        self.app_config.language = self._backup["language"]

    def restore_defaults(self):
        self.app_config.language = AppConfig().language
        self.setup_data()

    def setup_data(self):
        self._setup_language_data()

    def post_init(self):
        self.cb_language.currentIndexChanged.connect(self._language_changed)

    @property
    def _language_ui(self) -> QHBoxLayout:
        layout = QHBoxLayout()

        self._languages = [(ComboBox.tr("System"), "system"), ("English", "en"), ("Русский", "ru")]
        self.cb_language = ComboBox()
        for item in self._languages:
            self.cb_language.addItem(*item)

        self.l_language = Label(Label.tr("Language:"))

        layout.addWidget(self.l_language, 0, Qt.AlignLeft)
        layout.addWidget(self.cb_language, 1, Qt.AlignLeft)

        return layout

    def _setup_language_data(self):
        index = self.cb_language.findData(self.app_config.language)
        self.cb_language.setCurrentIndex(index)

    @Slot()
    def _language_changed(self, index: int):
        self.app_config.language = self._languages[index][1]
